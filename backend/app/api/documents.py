"""Upload / gestion des documents (UC03, UC06).

TODO: POST /api/documents/upload -> stocke le fichier (services.storage_service)
puis déclenche l'indexation (rag.chunking + rag.embeddings).
TODO: GET /api/documents -> liste des documents indexés + statut.
TODO: DELETE /api/documents/{id} -> suppression du document et de ses vecteurs.
"""
from fastapi import APIRouter

router = APIRouter()
