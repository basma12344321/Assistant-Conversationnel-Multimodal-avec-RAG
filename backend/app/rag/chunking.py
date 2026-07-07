"""Découpage des documents en chunks sémantiques.

Stratégie (cf. cahier des charges §4.3) :
- Taille cible : 512 à 1024 tokens, ici approximée en caractères (~4 caractères/token en moyenne)
- Chevauchement : 10-20% pour ne pas couper une idée entre deux chunks
- Découpage par paragraphes/phrases cohérents plutôt qu'à taille fixe brutale
"""
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 800 tokens ~ 3200 caractères (bonne valeur médiane dans la fourchette 512-1024 tokens)
DEFAULT_CHUNK_SIZE_CHARS = 3200
# 15% de chevauchement
DEFAULT_CHUNK_OVERLAP_CHARS = 480


@dataclass
class Chunk:
    text: str
    chunk_index: int
    source_filename: str
    metadata: dict = field(default_factory=dict)


def chunk_document(
    text: str,
    source_filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE_CHARS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP_CHARS,
) -> list[Chunk]:
    """Découpe un texte brut en chunks sémantiques cohérents.

    Le splitter essaie d'abord de couper aux sauts de paragraphe ("\\n\\n"),
    puis aux phrases, puis aux mots — dans cet ordre — pour éviter de couper
    au milieu d'une idée tant que possible.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)

    return [
        Chunk(
            text=raw_chunk,
            chunk_index=i,
            source_filename=source_filename,
            metadata={
                "filename": source_filename,
                "chunk_index": i,
                "char_count": len(raw_chunk),
            },
        )
        for i, raw_chunk in enumerate(raw_chunks)
    ]


if __name__ == "__main__":
    # Test rapide : lance `python -m app.rag.chunking` depuis backend/
    sample_text = (
        "Le RAG (Retrieval-Augmented Generation) permet d'ancrer les réponses d'un LLM "
        "dans une base documentaire interne.\n\n"
        "Cela réduit les hallucinations sur des sujets métier spécifiques et permet "
        "de citer les sources utilisées pour chaque réponse."
    )

    chunks = chunk_document(sample_text, source_filename="test.txt", chunk_size=100, chunk_overlap=20)
    for c in chunks:
        print(f"[{c.chunk_index}] ({c.metadata['char_count']} car.) {c.text[:80]}...")