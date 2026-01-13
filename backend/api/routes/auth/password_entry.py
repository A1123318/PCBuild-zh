# backend/api/routes/auth/password_entry.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as OrmSession

from backend.api.deps import get_db
from backend.services.auth.email_tokens import load_valid_token_and_user
from backend.services.auth.verification.core import (
    InvalidOrExpiredTokenError,
    VerificationPurpose,
)

router = APIRouter()


# ===== 忘記密碼：從 Email 連結進入重設頁面 =====
@router.get("/reset-password/{token}", name="reset_password")
def reset_password_entry(
    token: str,
    db: OrmSession = Depends(get_db),
):
    """
    忘記密碼 Email 連結入口。

    - token 有效：導向 /reset-password.html?token=...
    - token 無效/已失效（含過期、已使用、被取代、格式錯誤等）：一律導向失效頁
      （前端統一顯示「已失效」）
    """
    try:
        # 只驗證，不消費、不 commit；並套用 PASSWORD_RESET「僅最新 token 有效」規則
        load_valid_token_and_user(
            db=db,
            public_token=token,
            expected_purpose=VerificationPurpose.PASSWORD_RESET,
        )
    except InvalidOrExpiredTokenError:
        return RedirectResponse(
            url="/reset-password-failed.html",
            status_code=status.HTTP_302_FOUND,
        )

    return RedirectResponse(
        url=f"/reset-password.html?token={token}",
        status_code=status.HTTP_302_FOUND,
    )
