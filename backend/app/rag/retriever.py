"""Recherche hybride : dense (Qdrant/embeddings) + lexicale (BM25), fusionnées via RRF.

Le cahier des charges (§4.3) demande une recherche hybride sémantique + lexicale
avec fusion RRF (Reciprocal Rank Fusion). La recherche dense seule rate parfois
des correspondances exactes de mots-clés (ex. "GRANT", "CREATE ROLE") que BM25
retrouve très bien — les deux se complètent.
"""
from rank_bm25 import BM25Okapi

from app.config import settings
from app.db.vector_store import get_qdrant_client
from app.db.vector_store import search as dense_search
from app.rag.embeddings import embed_texts
from app.rag.reranker import rerank

RRF_K = 60  # constante standard de la fusion RRF (cf. littérature RRF)


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def _load_corpus() -> list[dict]:
    """Récupère tous les chunks indexés dans Qdrant (id + payload), nécessaire
    pour construire l'index BM25 à la volée à chaque requête.

    Limite connue : pour un très gros corpus, reconstruire BM25 à chaque appel
    devient coûteux. Acceptable pour la taille visée par le stage ; à revoir
    (cache, index BM25 persistant) si le volume de documents grossit beaucoup.
    """
    client = get_qdrant_client()
    corpus = []
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        corpus.extend({"id": p.id, "payload": p.payload} for p in points)
        if offset is None:
            break
    return corpus


def _bm25_search(query: str, corpus: list[dict], top_k: int) -> list[str]:
    """Retourne les ids des top_k chunks les plus pertinents selon BM25, triés."""
    if not corpus:
        return []
    tokenized_corpus = [_tokenize(item["payload"]["text"]) for item in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(query))
    ranked = sorted(zip(corpus, scores), key=lambda x: x[1], reverse=True)
    return [item["id"] for item, _score in ranked[:top_k]]


def retrieve(query: str, top_k: int = 5, candidates_per_method: int = 30, rerank_pool_size: int = 15) -> list[dict]:
    """Recherche hybride : dense (sémantique) + BM25 (lexicale), fusionnées par RRF,
    puis réévaluées finement par un cross-encoder (reranker.rerank).

    Retourne une liste de dicts triés par pertinence décroissante :
    [{"text", "filename", "section", "rrf_score", "rerank_score"}, ...]
    """
    query_vector = embed_texts([query])[0]

    dense_results = dense_search(query_vector, top_k=candidates_per_method)
    corpus = _load_corpus()
    bm25_ids = _bm25_search(query, corpus, top_k=candidates_per_method)

    rrf_scores: dict[str, float] = {}
    payloads: dict[str, dict] = {}

    for rank, point in enumerate(dense_results):
        rrf_scores[point.id] = rrf_scores.get(point.id, 0) + 1 / (RRF_K + rank + 1)
        payloads[point.id] = point.payload

    corpus_by_id = {item["id"]: item["payload"] for item in corpus}
    for rank, point_id in enumerate(bm25_ids):
        rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (RRF_K + rank + 1)
        payloads.setdefault(point_id, corpus_by_id.get(point_id))

    ranked_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:rerank_pool_size]

    candidates = [
        {
            "text": payloads[pid]["text"],
            "filename": payloads[pid]["filename"],
            "section": payloads[pid]["section"],
            "rrf_score": round(score, 4),
        }
        for pid, score in ranked_ids
        if payloads.get(pid) is not None
    ]

    return rerank(query, candidates, top_k=top_k)