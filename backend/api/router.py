# backend/api/router.py
from fastapi import APIRouter

from backend.api.auth import router as auth_router
from backend.api.chat import router as chat_router
from backend.api.debug import router as debug_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(debug_router)
api_router.include_router(auth_router)
