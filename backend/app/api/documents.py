"""Upload / gestion des documents (UC03, UC06).

STATUT ACTUEL : réponses mockées pour débloquer l'admin frontend.
TODO (backend) : brancher storage_service (upload), chunking + embeddings (indexation).
"""
from fastapi import APIRouter, UploadFile

from app.models.document_models import DocumentMetadata

router = APIRouter()

_MOCK_DOCUMENTS = [
    DocumentMetadata(id="1", filename="Cahier_des_Charges.pdf", status="indexed"),
    DocumentMetadata(id="2", filename="Architecture.docx", status="indexed"),
]


@router.get("/", response_model=list[DocumentMetadata])
def list_documents() -> list[DocumentMetadata]:
    return _MOCK_DOCUMENTS


@router.post("/upload", response_model=DocumentMetadata)
def upload_document(file: UploadFile) -> DocumentMetadata:
    # Mock — à remplacer par storage_service.save_file() + déclenchement indexation
    return DocumentMetadata(id="mock-id", filename=file.filename or "unknown", status="pending")