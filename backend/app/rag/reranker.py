"""Reranking des résultats via un cross-encoder (cahier des charges §4.3, optionnel).

Pourquoi une 2e passe après la fusion RRF : dense + BM25 comparent la requête
et chaque chunk indépendamment (rapide mais approximatif). Un cross-encoder lit
la requête ET le chunk ENSEMBLE en une seule passe, donnant un score de
pertinence bien plus fin — mais trop lent pour scorer tout le corpus, d'où son
usage seulement sur un petit lot de candidats déjà présélectionnés.
"""
from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.config import settings


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder(settings.reranker_model)


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Réordonne une liste de candidats (dicts avec au moins la clé "text")
    selon leur pertinence réelle par rapport à la requête.

    Retourne les top_k candidats triés par score de reranking décroissant,
    avec un champ supplémentaire "rerank_score" ajouté à chacun.
    """
    if not candidates:
        return []

    model = _get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)

    ranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_k]