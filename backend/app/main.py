from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Assistant Conversationnel Multimodal avec RAG",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


from app.api import chat, documents

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# TODO: brancher au fur et à mesure de leur implémentation (S3 pour ton binôme)
# from app.api import audio, images, auth
# app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
# app.include_router(images.router, prefix="/api/images", tags=["images"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
