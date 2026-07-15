"""Diagnostic : compare recherche dense seule, BM25 seule, et inspecte tous les
chunks de la section "Generating Your SSH Public Key" pour comprendre pourquoi
la fusion RRF ne la fait pas ressortir en tête.
"""
from app.config import settings
from app.db.vector_store import get_qdrant_client
from app.db.vector_store import search as dense_search
from app.rag.embeddings import embed_texts
from app.rag.retriever import _bm25_search, _load_corpus

query = "comment générer une clé SSH pour Git"

print("=== 1. Recherche DENSE seule (top 8) ===")
query_vector = embed_texts([query])[0]
for r in dense_search(query_vector, top_k=8):
    print(f"score={r.score:.4f} section=\"{r.payload['section']}\"")

print("\n=== 2. Recherche BM25 seule (top 8) ===")
corpus = _load_corpus()
bm25_ids = _bm25_search(query, corpus, top_k=8)
corpus_by_id = {item["id"]: item["payload"] for item in corpus}
for pid in bm25_ids:
    payload = corpus_by_id.get(pid)
    if payload:
        print(f"section=\"{payload['section']}\"")

print("\n=== 3. Tous les chunks de la section 'Generating Your SSH Public Key' ===")
matching = [item for item in corpus if item["payload"]["section"] == "Generating Your SSH Public Key"]
print(f"{len(matching)} chunk(s) trouvé(s) pour cette section :\n")
for item in matching:
    print(f"chunk_index={item['payload']['chunk_index']}")
    print(f"  {item['payload']['text'][:150]}")
    print()