"""Connexion Qdrant — indexation et recherche des chunks vectorisés.

Deux modes possibles (voir config.qdrant_mode) :
- "local"  : Qdrant embarqué, stocke tout sur disque dans qdrant_local_path.
             Aucun serveur/Docker requis — pratique en développement individuel.
- "server" : vrai serveur Qdrant (celui lancé par docker-compose), nécessaire
             dès que plusieurs process doivent accéder à la même base en même
             temps (ex. plusieurs workers uvicorn, ou déploiement en équipe).
"""
import hashlib
import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.rag.chunking import Chunk
from app.rag.embeddings import get_embedding_dimension


def _make_point_id(chunk: Chunk) -> str:
    """ID déterministe basé sur le contenu du chunk (fichier + section + index + texte).

    Pourquoi : réindexer le même document (même contenu) produit exactement
    les mêmes IDs, donc Qdrant écrase (upsert) les points existants au lieu
    d'en créer des doublons — pas besoin de vérifier "est-ce déjà indexé ?"
    avant d'appeler index_chunks().

    Limite connue : si le contenu d'un document change légèrement (nouvelle
    version), les anciens points ne portant plus les mêmes IDs restent en
    base (orphelins). Pour une vraie mise à jour de version, mieux vaut
    supprimer explicitement les anciens points du fichier avant réindexation
    (voir delete_document_chunks ci-dessous).
    """
    key = f"{chunk.source_filename}:{chunk.metadata.get('section')}:{chunk.chunk_index}:{chunk.text}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest[:32]))


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
            id=_make_point_id(chunk),
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


def delete_document_chunks(filename: str) -> None:
    """Supprime tous les chunks déjà indexés pour un fichier donné.

    À utiliser avant de réindexer un document dont le contenu a changé
    (nouvelle version) — les IDs déterministes de _make_point_id ne suffisent
    pas dans ce cas, car un contenu différent produit des IDs différents,
    laissant les anciens points orphelins si on ne les supprime pas explicitement.
    """
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        return
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))]),
    )


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