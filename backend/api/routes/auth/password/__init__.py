# backend/api/routes/auth/password/__init__.py
from fastapi import APIRouter

from backend.api.routes.auth.password.password_entry import router as password_entry_router
from backend.api.routes.auth.password.forgot_password import router as forgot_password_router
from backend.api.routes.auth.password.password_reset import router as password_reset_router

router = APIRouter()
router.include_router(password_entry_router)
router.include_router(forgot_password_router)
router.include_router(password_reset_router)

