"""RAG pipeline: semantic search → context assembly → grounding prompt → dual output.

Implements SDD 11.3 cross-reference check to prevent hallucinated citations.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.models.repository import RepositoryItem
from app.services import vector_store
from app.services.llm_gateway import generate

logger = logging.getLogger(__name__)

# ── Static no-context response (FR-AST-06) ──────────────────
NO_CONTEXT_RESPONSE: dict = {
    "detailedAnswer": (
        "I do not have enough verified NCPOR polar research records to answer "
        "this question. Please try a different question related to India's polar "
        "expeditions, stations, or research programmes."
    ),
    "simplifiedAnswer": (
        "I don't have enough information in the polar research archive to answer "
        "this yet. Try asking about an expedition, station, or a specific polar "
        "science topic."
    ),
    "usedSourceIds": [],
    "sources": [],
}

# ── Grounding system prompt ─────────────────────────────────
GROUNDING_SYSTEM_PROMPT = """\
You are POLARIS, the AI assistant for Polar Connect — India's polar science \
knowledge platform operated by NCPOR (National Centre for Polar and Ocean Research).

RULES:
1. Answer ONLY using the provided context passages. Never add knowledge from outside these passages.
2. If the context is insufficient, say so clearly.
3. Return your answer as a strict JSON object with exactly these keys:
   - "detailedAnswer": A comprehensive, well-structured answer (2-4 paragraphs).
   - "simplifiedAnswer": The same answer rewritten for a Class 10 student (1-2 short paragraphs, simple words).
   - "usedSourceIds": An array of doc_id strings from the context that you actually used.
4. Do NOT invent source IDs. Only use doc_id values that appear in the context below.
5. Do NOT wrap the JSON in markdown code fences. Return raw JSON only.

CONTEXT PASSAGES:
{context}
"""

SIMILARITY_THRESHOLD = 1.2  # cosine distance — lower = more similar


async def query_assistant(question: str, db: Session) -> dict:
    """Execute the full RAG pipeline."""

    # 1 ── Retrieve chunks from ChromaDB
    results = vector_store.query_chunks(query_text=question, n_results=4)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return NO_CONTEXT_RESPONSE

    # 2 ── Filter by distance threshold
    relevant_docs: list[str] = []
    relevant_metas: list[dict] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist <= SIMILARITY_THRESHOLD:
            relevant_docs.append(doc)
            relevant_metas.append(meta)

    if not relevant_docs:
        return NO_CONTEXT_RESPONSE

    # 3 ── Assemble context string
    seen_doc_ids: set[str] = set()
    context_parts: list[str] = []
    for i, (doc, meta) in enumerate(zip(relevant_docs, relevant_metas)):
        doc_id = meta.get("doc_id", f"unknown-{i}")
        seen_doc_ids.add(doc_id)
        context_parts.append(
            f'[Source doc_id="{doc_id}" type="{meta.get("type", "")}" '
            f'region="{meta.get("region", "")}"]\n{doc}'
        )
    context_text = "\n\n---\n\n".join(context_parts)

    # 4 ── Call LLM with grounding prompt
    system_prompt = GROUNDING_SYSTEM_PROMPT.format(context=context_text)
    try:
        raw_response = await generate(
            system_prompt=system_prompt,
            user_prompt=question,
            temperature=0.2,
        )
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        return NO_CONTEXT_RESPONSE

    # 5 ── Parse LLM JSON
    try:
        cleaned = raw_response.strip()
        # Strip markdown code fences if the model wrapped its reply
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        answer = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM JSON: %.200s", raw_response)
        answer = {
            "detailedAnswer": raw_response,
            "simplifiedAnswer": raw_response,
            "usedSourceIds": list(seen_doc_ids),
        }

    # 6 ── Cross-reference: only allow doc_ids that were actually retrieved
    used_ids = answer.get("usedSourceIds", [])
    validated_ids = [sid for sid in used_ids if sid in seen_doc_ids]

    # 7 ── Fetch source metadata from DB
    sources: list[dict] = []
    if validated_ids:
        items = (
            db.query(RepositoryItem)
            .filter(RepositoryItem.id.in_(validated_ids))
            .all()
        )
        sources = [
            {"id": it.id, "title": it.title, "type": it.type} for it in items
        ]

    return {
        "detailedAnswer": answer.get("detailedAnswer", ""),
        "simplifiedAnswer": answer.get("simplifiedAnswer", ""),
        "usedSourceIds": validated_ids,
        "sources": sources,
    }
