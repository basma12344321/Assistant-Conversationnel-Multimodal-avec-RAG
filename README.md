# Assistant Conversationnel Multimodal avec RAG

Assistant IA d'entreprise capable d'interagir en texte, image, audio et documents,
en s'appuyant sur une base de connaissances interne indexée (pipeline RAG).

Stack : **Python / FastAPI** (backend) + **React / Next.js** (frontend) + **Qdrant** (vecteurs) + **PostgreSQL** (relationnel)

## Démarrage rapide

```bash
git clone <url-du-repo>
cd assistant-rag-multimodal
cp backend/.env.example backend/.env   # à compléter avec vos clés
docker compose up --build
```

- Backend (API) : http://localhost:8000/docs
- Frontend : http://localhost:3000

## Structure du projet

```
backend/app/
  api/          routes HTTP (chat, documents, audio, images, auth)
  core/         sécurité (JWT) et dépendances FastAPI
  rag/          pipeline RAG (chunking, embeddings, retriever, reranker, prompt, orchestration)
  multimodal/   STT (Whisper), TTS, vision, extraction de documents
  models/       schémas Pydantic
  db/           connexions PostgreSQL et Qdrant
  services/     appels LLM, stockage fichiers

frontend/src/
  app/          pages Next.js (chat, login, admin)
  components/   composants UI (chat, upload, admin)
  hooks/        hooks React (useChat, useAudioRecorder)
  services/     appels API centralisés (api.ts)
```

## Documents de référence

Voir `docs/` : cahier des charges et document d'architecture détaillé.

## Équipe

- Backend & pipeline RAG : [ton nom]
- Frontend & multimodal : [nom du binôme]

## Conventions

- Commits : `type(scope): description` (ex. `feat(rag): add hybrid search`)
- Branches : `feature/<nom-fonctionnalite>`
- PR obligatoire avec revue de code avant fusion sur `main`
