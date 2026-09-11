"""ChromaDB client, collection init, chunk upsert & query.

Uses the persistent local client and ChromaDB's built-in default embedding
function (onnxruntime all-MiniLM-L6-v2) — no PyTorch required.
"""

from __future__ import annotations

import logging
from typing import Optional

import chromadb

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[chromadb.ClientAPI] = None
_collection = None
COLLECTION_NAME = "polar_docs"


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMADB_DIR)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(
    doc_id: str,
    chunks: list[str],
    metadatas: list[dict],
) -> None:
    """Upsert document chunks.  Wipes prior chunks for *doc_id* first (NFR-03)."""
    collection = get_collection()

    # Delete existing chunks for this document
    try:
        existing = collection.get(where={"doc_id": doc_id})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass  # collection may be empty

    # Add new chunks
    ids = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    logger.info("Indexed %d chunks for doc_id=%s", len(chunks), doc_id)


def query_chunks(
    query_text: str,
    n_results: int = 4,
    where: Optional[dict] = None,
) -> dict:
    """Semantic search against the vector store."""
    collection = get_collection()
    kwargs: dict = {"query_texts": [query_text], "n_results": n_results}
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)


def delete_doc_chunks(doc_id: str) -> None:
    """Remove all chunks belonging to *doc_id*."""
    collection = get_collection()
    try:
        existing = collection.get(where={"doc_id": doc_id})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
            logger.info("Deleted %d chunks for doc_id=%s", len(existing["ids"]), doc_id)
    except Exception as exc:
        logger.warning("Error deleting chunks for doc_id=%s: %s", doc_id, exc)
