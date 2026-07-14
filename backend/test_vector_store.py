"""Test manuel : indexation + recherche réelle dans Qdrant."""
from app.config import settings
from app.multimodal.document_parser import parse_document
from app.rag.chunking import chunk_sections
from app.rag.embeddings import embed_chunks
from app.db.vector_store import index_chunks, search

print(f"Mode Qdrant utilisé : {settings.qdrant_mode} (host={settings.qdrant_host}, port={settings.qdrant_port})")

sections = parse_document("../data/documents/guide_administration_test.md")
chunks = chunk_sections(sections, "guide_administration_test.md", chunk_size=300, chunk_overlap=50)
pairs = embed_chunks(chunks)

n = index_chunks(pairs)
print(f"{n} chunks indexés\n")

results = search(pairs[0][1], top_k=3)
print("Résultats de recherche :")
for r in results:
    print(f"  score={r.score:.3f} section=\"{r.payload['section']}\" texte={r.payload['text'][:60]}...")