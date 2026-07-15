"""Construction du prompt enrichi (requête + contexte récupéré).

Objectif clé : le prompt doit pousser le LLM à répondre UNIQUEMENT à partir
du contexte fourni (pour éviter les hallucinations, cf. cahier des charges
§1.2), et à citer la section précise de chaque passage utilisé (pas juste
le nom du fichier) — l'exigence formulée par l'encadrant.
"""

SYSTEM_PROMPT = """Tu es un assistant qui aide une équipe de développeurs à comprendre de la documentation technique.

Règles strictes :
- Réponds UNIQUEMENT à partir des extraits de documentation fournis ci-dessous. N'invente jamais d'information qui n'y figure pas.
- Si les extraits ne contiennent pas de quoi répondre à la question, dis-le clairement plutôt que d'improviser.
- Pour chaque affirmation, indique la source précise entre parenthèses, au format (fichier, section "titre de la section").
- Réponds dans la même langue que la question posée.
- Sois concret et actionnable : si la doc décrit une procédure, donne les étapes."""


def build_prompt(query: str, retrieved_chunks: list[dict]) -> dict:
    """Construit le prompt enrichi à partir de la requête et des chunks récupérés
    (sortie de retriever.retrieve()).

    Retourne {"system": str, "user": str} — format neutre, à adapter par
    llm_service.py selon l'API utilisée (OpenAI, Anthropic, LLM local...).
    """
    if not retrieved_chunks:
        context = "(Aucun extrait pertinent trouvé dans la base documentaire.)"
    else:
        context_parts = [
            f'[Extrait {i}] Source : {chunk["filename"]}, section "{chunk["section"]}"\n{chunk["text"]}'
            for i, chunk in enumerate(retrieved_chunks, start=1)
        ]
        context = "\n\n---\n\n".join(context_parts)

    user_prompt = f"""Voici des extraits de documentation technique :

{context}

Question : {query}

Réponds à la question en te basant uniquement sur ces extraits, et cite la source précise (fichier + section) pour chaque affirmation."""

    return {"system": SYSTEM_PROMPT, "user": user_prompt}


def extract_sources(retrieved_chunks: list[dict]) -> list[str]:
    """Construit la liste des sources utilisées, dédupliquée, dans l'ordre de
    pertinence — au format attendu par ChatResponse.sources
    (ex. "progit.pdf — Generating Your SSH Public Key"), avec la section
    précise plutôt que le seul nom de fichier.
    """
    seen = set()
    sources = []
    for chunk in retrieved_chunks:
        label = f"{chunk['filename']} — {chunk['section']}"
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return sources