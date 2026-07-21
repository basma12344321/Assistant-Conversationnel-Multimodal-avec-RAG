"""Endpoints conversation (UC01, UC03, UC07)."""
from fastapi import APIRouter

from app.models.chat_models import ChatRequest, ChatResponse
from app.rag.pipeline import run_rag_pipeline

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def send_message(payload: ChatRequest) -> ChatResponse:
    result = run_rag_pipeline(payload.message)
    return ChatResponse(answer=result["answer"], sources=result["sources"])