# backend/api/routes/auth/session/__init__.py
from fastapi import APIRouter

from backend.api.routes.auth.session.session_login import router as session_login_router
from backend.api.routes.auth.session.session_logout import router as session_logout_router
from backend.api.routes.auth.session.session_me import router as session_me_router

router = APIRouter()
router.include_router(session_login_router)
router.include_router(session_logout_router)
router.include_router(session_me_router)
