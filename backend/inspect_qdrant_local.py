"""Inspecte le contenu de la collection Qdrant en mode local (pas de dashboard
web disponible dans ce mode, contrairement au serveur Docker)."""
from app.config import settings
from app.db.vector_store import get_qdrant_client

client = get_qdrant_client()

if not client.collection_exists(settings.qdrant_collection):
    print(f"La collection '{settings.qdrant_collection}' n'existe pas encore.")
else:
    info = client.get_collection(settings.qdrant_collection)
    print(f"Collection : {settings.qdrant_collection}")
    print(f"Nombre total de points : {info.points_count}")
    print()

    points, _ = client.scroll(
        collection_name=settings.qdrant_collection,
        limit=10,
        with_payload=True,
        with_vectors=False,
    )
    print(f"Aperçu des {len(points)} premiers points :\n")
    for p in points:
        print(f"id={p.id}")
        print(f"  filename: {p.payload['filename']}")
        print(f"  section: {p.payload['section']}")
        print(f"  texte: {p.payload['text'][:80]}...")
        print()