# backend/api/routes/auth/verification.py
from fastapi import APIRouter

from backend.api.routes.auth.verify_email import router as verify_email_router
from backend.api.routes.auth.resend_verification import router as resend_verification_router

router = APIRouter()

router.include_router(verify_email_router)
router.include_router(resend_verification_router)
