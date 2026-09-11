"""Document ingestion pipeline: extract text → chunk → embed → store in ChromaDB."""

from __future__ import annotations

import logging
from pathlib import Path

from app.services import vector_store

logger = logging.getLogger(__name__)

# ── Chunking parameters ──────────────────────────────────────
CHUNK_SIZE_TOKENS = 600
CHUNK_OVERLAP_TOKENS = 100
CHARS_PER_TOKEN = 4  # rough approximation

CHUNK_CHARS = CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN       # ~2400
OVERLAP_CHARS = CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN   # ~400


def extract_text_from_file(file_path: str) -> str:
    """Extract plain text from PDF, TXT, or MD files."""
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".txt", ".md", ".markdown"):
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    else:
        logger.warning("Unsupported extension %s — attempting plain-text read", ext)
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def extract_text_from_raw(raw_text: str) -> str:
    """Pass-through for items that already have raw_text (seed data)."""
    return raw_text


def chunk_text(text: str) -> list[str]:
    """Split *text* into overlapping windows of ~CHUNK_SIZE_TOKENS tokens."""
    if not text or not text.strip():
        return []

    step = CHUNK_CHARS - OVERLAP_CHARS
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunk = text[start : start + CHUNK_CHARS].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def ingest_document(
    doc_id: str,
    file_path: str = "",
    raw_text: str = "",
    doc_type: str = "",
    region: str = "",
    year: int = 0,
) -> str:
    """Full pipeline: extract → chunk → store.  Returns ``'indexed'`` or ``'failed'``."""
    try:
        text = raw_text or (extract_text_from_file(file_path) if file_path else "")
        if not text.strip():
            logger.warning("No text for doc_id=%s", doc_id)
            return "failed"

        chunks = chunk_text(text)
        if not chunks:
            return "failed"

        metadatas = [
            {
                "doc_id": doc_id,
                "type": doc_type,
                "region": region,
                "year": str(year) if year else "",
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        vector_store.add_chunks(doc_id, chunks, metadatas)
        logger.info("Ingested %d chunks for doc_id=%s", len(chunks), doc_id)
        return "indexed"

    except Exception as exc:
        logger.error("Ingestion failed for doc_id=%s: %s", doc_id, exc)
        return "failed"


# ── Private helpers ──────────────────────────────────────────

def _extract_pdf(file_path: str) -> str:
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n\n".join(pages)
    except Exception as exc:
        logger.error("PDF extraction failed for %s: %s", file_path, exc)
        return ""
