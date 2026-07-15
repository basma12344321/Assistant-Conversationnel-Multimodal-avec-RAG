"""Test de la recherche hybride sur le vrai corpus Pro Git déjà indexé."""
from app.rag.retriever import retrieve

results = retrieve("comment générer une clé SSH pour Git", top_k=5)
print("Résultats de la recherche hybride :\n")
for r in results:
    print(f"score={r['score']:.4f}")
    print(f"  section: \"{r['section']}\"")
    print(f"  texte: {r['text'][:150]}...")
    print()