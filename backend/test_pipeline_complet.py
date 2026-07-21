"""Test du pipeline RAG complet (retrieve -> prompt -> LLM -> sources),
directement, sans passer par le serveur web FastAPI.
"""
from app.rag.pipeline import run_rag_pipeline

result = run_rag_pipeline("comment générer une clé SSH pour Git ?")

print("=== RÉPONSE ===")
print(result["answer"])
print()
print("=== SOURCES ===")
for s in result["sources"]:
    print(f"  - {s}")