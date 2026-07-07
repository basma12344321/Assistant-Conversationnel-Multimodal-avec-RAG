"""Schémas Pydantic pour la gestion des documents."""
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    status: str  # "pending" | "indexed" | "failed"
