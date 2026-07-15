"""Test de la recherche hybride + reranking sur le vrai corpus Pro Git déjà indexé."""
from app.rag.retriever import retrieve

results = retrieve("comment générer une clé SSH pour Git", top_k=5)
print("Résultats après RRF + reranking :\n")
for r in results:
    print(f"rrf={r['rrf_score']:.4f} rerank={r['rerank_score']:.2f}")
    print(f"  section: \"{r['section']}\"")
    print(f"  texte: {r['text'][:150]}...")
    print()