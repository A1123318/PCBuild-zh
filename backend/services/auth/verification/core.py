# backend/services/auth/verification/core.py
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from argon2 import PasswordHasher, exceptions as argon2_exceptions
from sqlalchemy.orm import Session

from backend.models import EmailVerificationToken


class VerificationPurpose(str, Enum):
    """驗證碼用途（目前使用 SIGNUP / PASSWORD_RESET）。"""
    SIGNUP = "signup"
    PASSWORD_RESET = "password_reset"


# 各用途預設有效時間（分鐘）
DEFAULT_LIFETIME_MINUTES: dict[VerificationPurpose, int] = {
    VerificationPurpose.SIGNUP: 24 * 60,        # 24 小時
    VerificationPurpose.PASSWORD_RESET: 20,     # 20 分鐘
}

# 各用途重新寄送最小間隔（分鐘）
RESEND_MIN_INTERVAL_MINUTES: dict[VerificationPurpose, int] = {
    VerificationPurpose.SIGNUP: 1,
    VerificationPurpose.PASSWORD_RESET: 1,
}


class VerificationEmailRateLimitedError(Exception):
    """在允許時間間隔內過度頻繁要求重新寄送時拋出。"""


class TokenState(str, Enum):
    INVALID = "invalid"
    EXPIRED = "expired"
    USED = "used"
    SUPERSEDED = "superseded"
    ALREADY_VERIFIED = "already_verified"


class InvalidOrExpiredTokenError(Exception):
    """token 驗證失敗（前端統一顯示已失效；後端用 state 區分原因）。"""

    def __init__(self, message: str = "驗證連結已失效。", *, state: TokenState = TokenState.INVALID):
        super().__init__(message)
        self.state = state


# 專用 Argon2id hasher，用來雜湊「驗證碼」
_token_hasher = PasswordHasher()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_token(secret: str) -> str:
    return _token_hasher.hash(secret)


def verify_token(secret: str, token_hash: str) -> bool:
    try:
        return _token_hasher.verify(token_hash, secret)
    except (
        argon2_exceptions.VerifyMismatchError,
        argon2_exceptions.VerificationError,
    ):
        return False
    except Exception:
        return False


def split_public_token(public_token: str) -> tuple[int, str]:
    """
    格式: "<id>.<secret>"
    """
    try:
        id_str, secret = public_token.split(".", 1)
        token_id = int(id_str)
    except (ValueError, AttributeError):
        raise InvalidOrExpiredTokenError("Token 格式不正確。")

    if not secret:
        raise InvalidOrExpiredTokenError("Token 格式不正確。")

    return token_id, secret


def resolve_lifetime_minutes(
    purpose: VerificationPurpose,
    override_minutes: int | None,
) -> int:
    if override_minutes is not None:
        return override_minutes
    return DEFAULT_LIFETIME_MINUTES[purpose]


def get_latest_token_for_user(
    db: Session,
    user_id: int,
    *,
    purpose: VerificationPurpose,
) -> EmailVerificationToken | None:
    return (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.purpose == purpose.value,
        )
        .order_by(EmailVerificationToken.created_at.desc())
        .first()
    )
