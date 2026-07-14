"""Génération des vecteurs d'embedding — pour les chunks à indexer ET pour les
requêtes utilisateur au moment de la recherche (retriever.py réutilisera embed_texts).

Modèle utilisé : config.settings.embedding_model (par défaut BAAI/bge-small-en-v1.5,
léger et rapide, suffisant pour un corpus de taille modeste comme celui du stage).
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.rag.chunking import Chunk


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    # Chargé une seule fois (modèle assez lourd à charger), puis réutilisé pour tous les appels
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Vectorise une liste de textes bruts.

    normalize_embeddings=True : les vecteurs sont normalisés (norme 1), ce qui
    permet d'utiliser la similarité cosinus directement dans Qdrant (retriever.py).
    """
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_chunks(chunks: list[Chunk]) -> list[tuple[Chunk, list[float]]]:
    """Vectorise une liste de chunks (sortie de chunking.chunk_sections).

    Retourne des paires (chunk, vecteur) prêtes à être envoyées à vector_store.py
    pour indexation dans Qdrant.
    """
    texts = [chunk.text for chunk in chunks]
    vectors = embed_texts(texts)
    return list(zip(chunks, vectors))


def get_embedding_dimension() -> int:
    """Dimension des vecteurs produits par le modèle — nécessaire à vector_store.py
    pour créer la collection Qdrant avec la bonne taille de vecteur.
    """
    model = _get_model()
    return model.get_sentence_embedding_dimension()