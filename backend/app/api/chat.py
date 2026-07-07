"""Endpoints conversation (UC01, UC03, UC07).

TODO: POST /api/chat -> reçoit un message, appelle app.rag.pipeline,
retourne la réponse générée + les sources utilisées.
"""
from fastapi import APIRouter

router = APIRouter()
