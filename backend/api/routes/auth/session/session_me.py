# backend/api/routes/auth/session/session_me.py
from fastapi import APIRouter, Depends

from backend.api.dependencies.auth import get_current_user
from backend.models import User

router = APIRouter()


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    # 回傳欄位需符合前端既有使用（email/username/is_active）
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_active": current_user.is_active,
    }
