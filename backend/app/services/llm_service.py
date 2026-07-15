"""Appels au LLM (GPT-4o / Claude / local selon config.llm_provider).

Design en interface abstraite : le reste du pipeline (pipeline.py) appelle
generate_response(prompt) sans savoir quel fournisseur est utilisé derrière.
Permet de changer de fournisseur (cloud <-> LLM local type Ollama) sans
toucher au reste du code — utile tant que la décision on-premise vs cloud
n'est pas tranchée avec l'encadrant.
"""
from app.config import settings


def generate_response(prompt: dict) -> str:
    """Génère une réponse à partir du prompt (sortie de prompt_builder.build_prompt,
    un dict {"system": str, "user": str}).

    Le fournisseur utilisé dépend de settings.llm_provider ("groq" | "openai" | "anthropic" | "local").
    """
    if settings.llm_provider == "groq":
        return _generate_groq(prompt)
    if settings.llm_provider == "openai":
        return _generate_openai(prompt)
    if settings.llm_provider == "anthropic":
        return _generate_anthropic(prompt)
    if settings.llm_provider == "local":
        return _generate_local(prompt)
    raise ValueError(f"llm_provider inconnu : {settings.llm_provider}")


def _generate_groq(prompt: dict) -> str:
    """Groq : palier gratuit généreux, sans carte bancaire. Compatible avec le
    SDK OpenAI — seule l'URL de base change, pas de nouvelle dépendance requise.
    """
    from openai import OpenAI

    client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def _generate_openai(prompt: dict) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def _generate_anthropic(prompt: dict) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=prompt["system"],
        messages=[{"role": "user", "content": prompt["user"]}],
    )
    return response.content[0].text


def _generate_local(prompt: dict) -> str:
    """Placeholder pour un LLM local (ex. Ollama). À implémenter une fois la
    décision on-premise vs cloud confirmée avec l'encadrant.
    """
    raise NotImplementedError(
        "Mode LLM local pas encore implémenté. "
        "Utilise llm_provider='groq', 'openai' ou 'anthropic' en attendant."
    )