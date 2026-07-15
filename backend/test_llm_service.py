"""Test isolé de llm_service.py : appelle directement generate_response()
avec un prompt simple, sans passer par retriever/prompt_builder.
Sert à valider que la clé API Groq fonctionne avant de tester tout le pipeline.
"""
from app.services.llm_service import generate_response

prompt = {
    "system": "Tu es un assistant utile qui répond de façon concise.",
    "user": "Explique en une phrase ce qu'est Git.",
}

answer = generate_response(prompt)
print("Réponse du LLM :")
print(answer)