# backend/api/routes/auth/password/password_reset.py
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session as OrmSession

from backend.api.dependencies.db import get_db
from backend.api.auth_utils import clear_session_cookie, raise_400
from backend.models import Session as SessionModel
from backend.schemas.auth import ResetPasswordIn
from backend.security import hash_password, verify_password
from backend.services.auth.email_tokens import consume_verification_token
from backend.services.auth.verification.core import (
    InvalidOrExpiredTokenError,
    VerificationPurpose,
)
from backend.core.middleware.rate_limit import limiter

router = APIRouter()


# ===== 忘記密碼：重設密碼 =====
@router.post("/reset-password")
@limiter.shared_limit("20/minute", scope="auth_sensitive")
@limiter.limit("5/minute")
def reset_password(
    body: ResetPasswordIn,
    request: Request,  # ← 新增（即使函式內不用）
    response: Response,
    db: OrmSession = Depends(get_db),
):
    try:
        user, _token = consume_verification_token(
            db,
            body.token,
            purpose=VerificationPurpose.PASSWORD_RESET,
        )
    except InvalidOrExpiredTokenError:
        raise_400({"token": "重設密碼連結無效或已過期，請重新申請。"})
        raise

    if verify_password(body.password, user.password_hash):
        db.rollback()
        raise_400({"password": "新密碼不可與原密碼相同，請重新設定。"})

    user.password_hash = hash_password(body.password)

    if not user.is_active:
        user.is_active = True

    db.query(SessionModel).filter(
        SessionModel.user_id == user.id,
        SessionModel.revoked.is_(False),
    ).update(
        {"revoked": True},
        synchronize_session=False,
    )

    db.commit()

    clear_session_cookie(response)
    return {"ok": True}
