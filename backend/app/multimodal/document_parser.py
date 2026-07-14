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

    Priorité 1 : signets/marque-pages intégrés au PDF (l'"outline"). Comme
    beaucoup de PDF n'ont des signets qu'au niveau chapitre, on affine ensuite
    en détectant les sous-titres à l'intérieur de chaque chapitre (texte en
    police plus grande/grasse que le corps), pour des citations plus précises
    (ex. "What is Git? — Nearly Every Operation Is Local" plutôt qu'un seul
    gros bloc "What is Git?").
    Priorité 2 (repli) : si le PDF n'a aucun signet, une section par page.
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

        located = []
        for title, page_index in bookmarks:
            if page_index >= total_pages:
                continue
            top = _find_heading_top(pdf.pages[page_index], title)
            located.append({"title": title, "page": page_index, "top": top})

        located.sort(key=lambda x: (x["page"], x["top"]))

        # Affinage : détecte les sous-titres à l'intérieur de chaque section
        # top-level (le PDF n'a souvent des signets qu'au niveau chapitre).
        body_size = _estimate_body_font_size(pdf)
        all_items = list(located)
        for idx, item in enumerate(located):
            next_item = located[idx + 1] if idx + 1 < len(located) else None
            all_items.extend(_detect_subheadings(pdf, item, next_item, total_pages, body_size))

        all_items.sort(key=lambda x: (x["page"], x["top"]))

        sections = []
        for idx, item in enumerate(all_items):
            next_item = all_items[idx + 1] if idx + 1 < len(all_items) else None
            text = _extract_section_text(pdf, item, next_item, total_pages)
            if text.strip():
                sections.append(Section(title=item["title"], text=text.strip()))

        return sections


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _find_heading_top(page, title: str) -> float:
    """Cherche la position verticale ('top') du titre sur une page.

    Un même texte peut apparaître deux fois sur une page : une fois comme
    titre (police plus grande), une fois cité dans un paragraphe du corps
    (police normale). Pour ne pas confondre les deux, on récupère TOUTES les
    occurrences du titre sur la page puis on garde celle dont la taille de
    police est la plus grande. Si toutes les occurrences ont la même taille,
    on garde la première rencontrée. Retourne 0.0 si introuvable.
    """
    words = page.extract_words(extra_attrs=["size"])
    if not words:
        return 0.0

    target = _normalize_text(title)
    target_tokens = target.split()
    if not target_tokens:
        return 0.0

    page_tokens = [(_normalize_text(w["text"]), w["top"], w.get("size", 0)) for w in words]
    n = len(target_tokens)

    candidates = []
    for i in range(len(page_tokens) - n + 1):
        window = page_tokens[i : i + n]
        window_text = " ".join(tok for tok, _, _ in window)
        if window_text == target:
            avg_size = sum(sz for _, _, sz in window) / n
            candidates.append((avg_size, page_tokens[i][1]))

    if not candidates:
        return 0.0

    max_size = max(c[0] for c in candidates)
    for avg_size, top in candidates:
        if avg_size == max_size:
            return top

    return candidates[0][1]


def _extract_section_text(pdf, item: dict, next_item: dict | None, total_pages: int) -> str:
    """Extrait le texte d'une section, du titre courant jusqu'au titre suivant
    (ou fin de document), avec découpage précis au niveau de la position
    verticale — pas seulement au niveau de la page entière.
    """
    start_page, start_top = item["page"], item["top"]
    end_page = next_item["page"] if next_item else total_pages - 1
    end_top = next_item["top"] if next_item else None

    parts = []

    if start_page == end_page and end_top is not None:
        page = pdf.pages[start_page]
        cropped = page.within_bbox((0, start_top, page.width, max(end_top, start_top)))
        parts.append(cropped.extract_text() or "")
    else:
        first_page = pdf.pages[start_page]
        cropped = first_page.within_bbox((0, start_top, first_page.width, first_page.height))
        parts.append(cropped.extract_text() or "")

        for p in range(start_page + 1, end_page):
            parts.append(pdf.pages[p].extract_text() or "")

        if end_page < total_pages and end_page != start_page:
            last_page = pdf.pages[end_page]
            top_limit = end_top if end_top is not None else last_page.height
            cropped = last_page.within_bbox((0, 0, last_page.width, max(top_limit, 0.1)))
            parts.append(cropped.extract_text() or "")

    return "\n\n".join(p.strip() for p in parts if p and p.strip())

def _estimate_body_font_size(pdf) -> float:
    """Estime la taille de police du corps de texte du document (la plus
    fréquente), en échantillonnant un lot de pages internes plutôt que la
    première/dernière page (souvent atypiques : couverture, table des
    matières...).
    """
    from collections import Counter

    sizes = Counter()
    pages = pdf.pages
    sample = pages[10:60] if len(pages) > 60 else pages
    for page in sample:
        for w in page.extract_words(extra_attrs=["size"]):
            sizes[round(w["size"], 1)] += 1

    if not sizes:
        return 11.0
    return sizes.most_common(1)[0][0]


def _detect_subheadings(pdf, parent_item: dict, next_item: dict | None, total_pages: int, body_size: float) -> list[dict]:
    """Cherche des sous-titres à l'intérieur d'une section (entre le titre
    de la section et le titre suivant), en repérant les lignes en police
    plus grande et/ou grasse que le corps du texte — typique des sous-titres
    dans un PDF sans signet dédié pour chaque sous-partie.
    """
    start_page, start_top = parent_item["page"], parent_item["top"]
    end_page = next_item["page"] if next_item else total_pages - 1
    end_top = next_item["top"] if next_item else None

    results = []
    for p in range(start_page, end_page + 1):
        page = pdf.pages[p]
        words = page.extract_words(extra_attrs=["size", "fontname"])
        if not words:
            continue

        lines: dict[float, list] = {}
        for w in words:
            key = round(w["top"])
            lines.setdefault(key, []).append(w)

        for top_key in sorted(lines):
            ws = sorted(lines[top_key], key=lambda w: w["x0"])
            top = ws[0]["top"]

            if p == start_page and top <= start_top + 1:
                continue  # c'est le titre de la section elle-même
            if p == end_page and end_top is not None and top >= end_top - 1:
                continue  # on est déjà entré dans la section suivante

            avg_size = sum(w["size"] for w in ws) / len(ws)
            is_bold = any("bold" in (w.get("fontname") or "").lower() for w in ws)
            word_count = len(ws)

            text = " ".join(w["text"] for w in ws)
            has_real_words = bool(re.search(r"[A-Za-z]{3,}", text))

            looks_like_heading = (
                word_count <= 12
                and avg_size > body_size * 1.1
                and (is_bold or avg_size > body_size * 1.3)
                and has_real_words
            )
            if looks_like_heading:
                results.append({
                    "title": f"{parent_item['title']} — {text}",
                    "page": p,
                    "top": top,
                })

    return results

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