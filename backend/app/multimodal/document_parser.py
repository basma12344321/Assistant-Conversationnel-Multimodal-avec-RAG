"""Extraction de texte depuis PDF / DOCX / CSV / Markdown / TXT.

Objectif clé (précisé par l'encadrant) : la citation de source finale doit
indiquer une SECTION précise (ex. "section RBAC"), pas juste le nom du fichier.
Ce module extrait donc le texte regroupé par section quand c'est possible,
pas juste un bloc de texte brut.

Fiabilité de la détection de section, du plus fiable au moins fiable :
- Markdown / TXT  : titres explicites ("# ", "## ", ...) -> fiable
- DOCX            : styles de titre Word (Heading 1, Heading 2...) -> fiable
- PDF             : pas de structure sémantique native -> on utilise la page
                     comme "section" par défaut (moins précis, mais robuste).
                     Amélioration possible plus tard : heuristique par taille de police.
"""
import re
from dataclasses import dataclass


@dataclass
class Section:
    title: str
    text: str


def parse_document(file_path: str) -> list[Section]:
    """Point d'entrée générique : choisit le bon parseur selon l'extension."""
    if file_path.endswith((".md", ".txt")):
        return _parse_markdown_or_txt(file_path)
    if file_path.endswith(".docx"):
        return _parse_docx(file_path)
    if file_path.endswith(".pdf"):
        return _parse_pdf(file_path)
    if file_path.endswith(".csv"):
        return _parse_csv(file_path)
    raise ValueError(f"Format non supporté : {file_path}")


def _parse_markdown_or_txt(file_path: str) -> list[Section]:
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    # Découpe sur les titres markdown ("#", "##", "###"...)
    parts = re.split(r"(?m)^(#{1,6}\s+.+)$", text)

    if len(parts) == 1:
        # Aucun titre trouvé : tout le fichier est une seule section
        return [Section(title="Document entier", text=text.strip())]

    sections: list[Section] = []
    # parts[0] = texte avant le premier titre (souvent vide ou intro)
    intro = parts[0].strip()
    if intro:
        sections.append(Section(title="Introduction", text=intro))

    for i in range(1, len(parts), 2):
        title = parts[i].lstrip("#").strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if body:
            sections.append(Section(title=title, text=body))

    return sections


def _parse_docx(file_path: str) -> list[Section]:
    from docx import Document

    doc = Document(file_path)
    sections: list[Section] = []
    current_title = "Introduction"
    current_body: list[str] = []

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading") and para.text.strip():
            # On ferme la section précédente avant d'en ouvrir une nouvelle
            if current_body:
                sections.append(Section(title=current_title, text="\n".join(current_body).strip()))
            current_title = para.text.strip()
            current_body = []
        elif para.text.strip():
            current_body.append(para.text)

    if current_body:
        sections.append(Section(title=current_title, text="\n".join(current_body).strip()))

    return sections


def _parse_pdf(file_path: str) -> list[Section]:
    """Extrait le texte d'un PDF, structuré par section quand c'est possible.

    Priorité 1 : signets/marque-pages intégrés au PDF (l'"outline", visible comme
    la table des matières cliquable dans un lecteur PDF). C'est une vraie structure
    posée par l'auteur du document — bien plus fiable qu'une heuristique.
    Priorité 2 (repli) : si le PDF n'a aucun signet, une section par page,
    comme avant — moins précis, mais ça reste exploitable.
    """
    import pdfplumber
    import pypdf

    reader = pypdf.PdfReader(file_path)
    bookmarks = _flatten_pdf_outline(reader)

    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

        if not bookmarks:
            sections: list[Section] = []
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    sections.append(Section(title=f"Page {i}", text=text.strip()))
            return sections

        sections = []
        for idx, (title, start_page) in enumerate(bookmarks):
            end_page = bookmarks[idx + 1][1] if idx + 1 < len(bookmarks) else total_pages
            page_texts = [
                (pdf.pages[p].extract_text() or "").strip()
                for p in range(start_page, min(end_page, total_pages))
            ]
            body = "\n\n".join(t for t in page_texts if t)
            if body:
                sections.append(Section(title=title, text=body))

        return sections


def _flatten_pdf_outline(reader) -> list[tuple[str, int]]:
    """Aplatit les signets d'un PDF en liste [(titre, index_page), ...] triée par page.

    Retourne une liste vide si le PDF n'a pas de signets (fera basculer sur le
    découpage par page dans _parse_pdf).
    """
    flat: list[tuple[str, int]] = []

    def _walk(items):
        for item in items:
            if isinstance(item, list):
                _walk(item)
            else:
                try:
                    page_num = reader.get_destination_page_number(item)
                    flat.append((item.title, page_num))
                except Exception:
                    continue

    try:
        _walk(reader.outline)
    except Exception:
        return []

    flat.sort(key=lambda x: x[1])
    return flat

def _parse_csv(file_path: str) -> list[Section]:
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return [Section(title="Document entier", text=text.strip())]