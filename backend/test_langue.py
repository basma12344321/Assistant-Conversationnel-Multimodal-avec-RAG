"""Teste la même question en anglais, pour vérifier si le désalignement de
langue (requête FR vs corpus Pro Git en EN) explique les mauvais scores de reranking.
"""
from app.rag.retriever import retrieve

results = retrieve("how to generate an SSH key for Git", top_k=5)
print("Résultats en anglais :\n")
for r in results:
    print(f"rrf={r['rrf_score']:.4f} rerank={r['rerank_score']:.2f}")
    print(f"  section: {r['section']}")
    print(f"  texte: {r['text'][:100]}")
    print()