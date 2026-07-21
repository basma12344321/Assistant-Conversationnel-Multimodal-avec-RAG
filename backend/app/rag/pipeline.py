"""Orchestration RAG complète : retrieve -> build_prompt -> generate_response.

Point d'entrée unique du pipeline, appelé par api/chat.py pour remplacer
la réponse mockée par la vraie génération RAG.
"""
from app.rag.prompt_builder import build_prompt, extract_sources
from app.rag.retriever import retrieve
from app.services.llm_service import generate_response


def run_rag_pipeline(query: str, top_k: int = 5) -> dict:
    """Exécute le pipeline RAG complet pour une question donnée.

    Retourne {"answer": str, "sources": list[str]} — format directement
    compatible avec le modèle Pydantic ChatResponse (models/chat_models.py).
    """
    retrieved_chunks = retrieve(query, top_k=top_k)
    prompt = build_prompt(query, retrieved_chunks)
    answer = generate_response(prompt)
    sources = extract_sources(retrieved_chunks)

    return {"answer": answer, "sources": sources}