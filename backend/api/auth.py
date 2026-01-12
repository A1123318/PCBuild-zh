# backend/api/auth.py
from fastapi import APIRouter

from backend.api.routes.auth.session import router as session_router
from backend.api.routes.auth.verification import router as verification_router
from backend.api.routes.auth.password import router as password_router
from backend.api.routes.auth.register import router as register_router

router = APIRouter(prefix="/api/auth", tags=["auth"])

router.include_router(session_router)
router.include_router(verification_router)
router.include_router(password_router)
router.include_router(register_router)