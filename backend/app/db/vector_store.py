"""Connexion Qdrant — indexation et recherche des chunks vectorisés.

Deux modes possibles (voir config.qdrant_mode) :
- "local"  : Qdrant embarqué, stocke tout sur disque dans qdrant_local_path.
             Aucun serveur/Docker requis — pratique en développement individuel.
- "server" : vrai serveur Qdrant (celui lancé par docker-compose), nécessaire
             dès que plusieurs process doivent accéder à la même base en même
             temps (ex. plusieurs workers uvicorn, ou déploiement en équipe).
"""
import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.rag.chunking import Chunk
from app.rag.embeddings import get_embedding_dimension


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    if settings.qdrant_mode == "local":
        return QdrantClient(path=settings.qdrant_local_path)
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection() -> None:
    """Crée la collection si elle n'existe pas encore (idempotent, sans effet si déjà là)."""
    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=get_embedding_dimension(), distance=Distance.COSINE),
        )


def index_chunks(pairs: list[tuple[Chunk, list[float]]]) -> int:
    """Indexe une liste de (chunk, vecteur) dans Qdrant. Base cumulative :
    chaque appel AJOUTE des points, n'écrase jamais ce qui existe déjà.
    Retourne le nombre de chunks indexés.
    """
    ensure_collection()
    client = get_qdrant_client()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk.text,
                "filename": chunk.source_filename,
                "section": chunk.metadata.get("section"),
                "chunk_index": chunk.chunk_index,
            },
        )
        for chunk, vector in pairs
    ]

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search(query_vector: list[float], top_k: int = 5):
    """Recherche les top_k chunks les plus proches d'un vecteur de requête.
    Utilisé par retriever.py (prochaine étape).
    Retourne une liste d'objets avec .score et .payload (text, filename, section, chunk_index).
    """
    ensure_collection()
    client = get_qdrant_client()
    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
    )
    return response.points