"""Repart d'une collection totalement propre et réindexe progit.pdf avec une
taille de chunk conforme au cahier des charges (512-1024 tokens, soit environ
2000-4000 caractères) au lieu du chunk_size=800 trop petit utilisé au premier essai.
"""
from app.config import settings
from app.db.vector_store import get_qdrant_client, index_chunks
from app.multimodal.document_parser import parse_document
from app.rag.chunking import chunk_sections
from app.rag.embeddings import embed_chunks

#NB_SECTIONS_A_INDEXER = 40

client = get_qdrant_client()
if client.collection_exists(settings.qdrant_collection):
    client.delete_collection(settings.qdrant_collection)
    print("Collection vidée (repart de zéro, plus de pollution croisée)")

print("Extraction des sections depuis progit.pdf...")
all_sections = parse_document("../data/documents/progit.pdf")
sections = all_sections  # document complet cette fois (394 sections fines)
print(f"{len(sections)} sections retenues (document complet)")

chunks = chunk_sections(sections, source_filename="progit.pdf")
print(f"{len(chunks)} chunks générés (moins fragmentés qu'avant)")

pairs = embed_chunks(chunks)
n = index_chunks(pairs)
print(f"{n} chunks indexés")