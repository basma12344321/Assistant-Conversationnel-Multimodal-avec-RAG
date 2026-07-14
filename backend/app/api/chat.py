"""Endpoints conversation (UC01, UC03, UC07).

STATUT ACTUEL : réponse mockée pour débloquer le frontend.
TODO (backend) : remplacer le corps de send_message() par un appel à
app.rag.pipeline.run_rag_pipeline(payload.message) une fois le pipeline prêt.
Le format de retour (ChatResponse) ne doit pas changer entre-temps.
"""
from fastapi import APIRouter

from app.models.chat_models import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def send_message(payload: ChatRequest) -> ChatResponse:
    # Mock — à remplacer par rag.pipeline.run_rag_pipeline(payload.message)
    return ChatResponse(
        answer=f"[Réponse simulée] Vous avez demandé : {payload.message}",
        sources=["Cahier_des_Charges.pdf", "Architecture.docx"],
    )