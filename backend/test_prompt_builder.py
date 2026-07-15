"""Test : build_prompt + extract_sources sur une vraie recherche."""
from app.rag.retriever import retrieve
from app.rag.prompt_builder import build_prompt, extract_sources

chunks = retrieve("comment générer une clé SSH pour Git", top_k=3)

prompt = build_prompt("comment générer une clé SSH pour Git", chunks)
print("=== PROMPT USER ===")
print(prompt["user"])
print()

sources = extract_sources(chunks)
print("=== SOURCES ===")
for s in sources:
    print(f"  - {s}")