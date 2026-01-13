# backend/services/auth/verification/token.py
from __future__ import annotations

from datetime import datetime, timezone

from argon2 import PasswordHasher, exceptions as argon2_exceptions

from backend.services.auth.verification.types import InvalidOrExpiredTokenError


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
