"""Schémas Pydantic pour les endpoints chat."""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
