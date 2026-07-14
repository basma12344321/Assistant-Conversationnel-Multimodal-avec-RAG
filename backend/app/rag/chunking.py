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
    """Découpe un texte brut (sans notion de section) en chunks sémantiques.

    À utiliser seulement si le document n'a pas de structure de sections
    (cas rare depuis document_parser.py) — sinon préférer chunk_sections().
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


def chunk_sections(
    sections: list,  # list[app.multimodal.document_parser.Section]
    source_filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE_CHARS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP_CHARS,
) -> list[Chunk]:
    """Découpe une liste de sections (sortie de document_parser.parse_document)
    en chunks, SANS jamais faire chevaucher deux sections dans un même chunk.

    Chaque chunk garde le titre de sa section d'origine en métadonnée
    (clé "section"), ce qui permet la citation précise attendue
    (ex. "section Gestion des rôles et permissions") plutôt qu'un simple nom
    de fichier.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Chunk] = []
    global_index = 0

    for section in sections:
        raw_chunks = splitter.split_text(section.text)
        for raw_chunk in raw_chunks:
            all_chunks.append(
                Chunk(
                    text=raw_chunk,
                    chunk_index=global_index,
                    source_filename=source_filename,
                    metadata={
                        "filename": source_filename,
                        "section": section.title,
                        "chunk_index": global_index,
                        "char_count": len(raw_chunk),
                    },
                )
            )
            global_index += 1

    return all_chunks


if __name__ == "__main__":
    # Test rapide : lance `python -m app.rag.chunking` depuis backend/
    # après avoir mis un .txt de test dans data/documents/
    sample_text = (
        "Le RAG (Retrieval-Augmented Generation) permet d'ancrer les réponses d'un LLM "
        "dans une base documentaire interne.\n\n"
        "Cela réduit les hallucinations sur des sujets métier spécifiques et permet "
        "de citer les sources utilisées pour chaque réponse."
    )

    chunks = chunk_document(sample_text, source_filename="test.txt", chunk_size=100, chunk_overlap=20)
    for c in chunks:
        print(f"[{c.chunk_index}] ({c.metadata['char_count']} car.) {c.text[:80]}...")