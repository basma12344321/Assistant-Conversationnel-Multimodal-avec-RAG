"""Indexe progit.pdf (un sous-ensemble de sections) dans le vrai Qdrant Docker.
Repart d'une collection propre pour éviter les doublons entre essais.
"""
from app.config import settings
from app.db.vector_store import get_qdrant_client, index_chunks
from app.multimodal.document_parser import parse_document
from app.rag.chunking import chunk_sections
from app.rag.embeddings import embed_chunks

NB_SECTIONS_A_INDEXER = 150  # augmente progressivement si tout se passe bien

client = get_qdrant_client()
if client.collection_exists(settings.qdrant_collection):
    client.delete_collection(settings.qdrant_collection)

print("Extraction des sections depuis progit.pdf...")
all_sections = parse_document("../data/documents/progit.pdf")
print(f"{len(all_sections)} sections trouvées au total, on en indexe {NB_SECTIONS_A_INDEXER}")

sections = all_sections[:NB_SECTIONS_A_INDEXER]
chunks = chunk_sections(sections, source_filename="progit.pdf", chunk_size=800, chunk_overlap=150)
print(f"{len(chunks)} chunks générés, génération des embeddings en cours (peut prendre 1-2 min)...")

pairs = embed_chunks(chunks)
n = index_chunks(pairs)
print(f"\n{n} chunks indexés dans Qdrant avec succès.")

info = client.get_collection(settings.qdrant_collection)
print(f"Total de points dans la collection : {info.points_count}")