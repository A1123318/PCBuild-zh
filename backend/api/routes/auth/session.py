# backend/api/routes/auth/session.py
from fastapi import APIRouter

from backend.api.routes.auth.session_login import router as session_login_router
from backend.api.routes.auth.session_logout import router as session_logout_router

router = APIRouter()

router.include_router(session_login_router)
router.include_router(session_logout_router)
