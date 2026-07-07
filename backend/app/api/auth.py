"""Login / gestion des utilisateurs.

TODO: POST /api/auth/login -> vérifie les identifiants, retourne un JWT (core.security).
TODO: POST /api/auth/register (si applicable).
"""
from fastapi import APIRouter

router = APIRouter()
