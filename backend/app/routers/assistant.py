"""/api/assistant — RAG query pipeline (public, no auth required)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse
from app.services.assistant_rag import query_assistant

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/query", response_model=AssistantQueryResponse)
async def query(body: AssistantQueryRequest, db: Session = Depends(get_db)):
    """Public endpoint — embed question, retrieve context, ground answer."""
    result = await query_assistant(body.question, db)
    return AssistantQueryResponse(**result)
