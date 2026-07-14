from app.multimodal.document_parser import parse_document
from app.rag.chunking import chunk_sections
from app.rag.embeddings import embed_chunks, get_embedding_dimension

sections = parse_document("../data/documents/guide_administration_test.md")
chunks = chunk_sections(sections, "guide_administration_test.md", chunk_size=300, chunk_overlap=50)
pairs = embed_chunks(chunks)

print(f"Dimension des vecteurs : {get_embedding_dimension()}")
print(f"Nombre total de paires (chunk, vecteur) : {len(pairs)}")
for chunk, vector in pairs:
    section = chunk.metadata["section"]
    print(f"section={section} vecteur[:5]={vector[:5]}")