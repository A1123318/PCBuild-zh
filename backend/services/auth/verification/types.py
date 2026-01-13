# backend/services/auth/verification/types.py
from __future__ import annotations

from enum import Enum


class VerificationPurpose(str, Enum):
    """驗證碼用途（目前使用 SIGNUP / PASSWORD_RESET）。"""
    SIGNUP = "signup"
    PASSWORD_RESET = "password_reset"


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
