"""Test rapide sur progit.pdf, limité aux premières sections pour aller vite."""
from app.multimodal.document_parser import parse_document
from app.rag.chunking import chunk_sections
from app.rag.embeddings import embed_chunks, get_embedding_dimension

NB_SECTIONS_A_TESTER = 5

all_sections = parse_document("../data/documents/progit.pdf")
print(f"{len(all_sections)} sections trouvées au total dans le PDF")

sections = all_sections[:NB_SECTIONS_A_TESTER]
print(f"On en garde {len(sections)} pour ce test :")
for s in sections:
    print(f"  - \"{s.title}\" ({len(s.text)} car.)")

chunks = chunk_sections(sections, source_filename="progit.pdf", chunk_size=800, chunk_overlap=150)
pairs = embed_chunks(chunks)

print(f"\nDimension des vecteurs : {get_embedding_dimension()}")
print(f"Nombre total de chunks générés et vectorisés : {len(pairs)}")
for chunk, vector in pairs[:3]:
    section = chunk.metadata["section"]
    print(f"section=\"{section}\" vecteur[:5]={vector[:5]}")
    