# backend/services/auth/verification/core.py
from __future__ import annotations

from backend.services.auth.verification.types import (
    VerificationPurpose,
    VerificationEmailRateLimitedError,
    TokenState,
    InvalidOrExpiredTokenError,
)
from backend.services.auth.verification.token import (
    utcnow,
    hash_token,
    verify_token,
    split_public_token,
)
from backend.services.auth.verification.repo import (
    DEFAULT_LIFETIME_MINUTES,
    RESEND_MIN_INTERVAL_MINUTES,
    resolve_lifetime_minutes,
    get_latest_token_for_user,
    get_resend_min_interval_minutes,
    get_resend_min_interval_seconds,
)

__all__ = [
    "VerificationPurpose",
    "VerificationEmailRateLimitedError",
    "TokenState",
    "InvalidOrExpiredTokenError",
    "DEFAULT_LIFETIME_MINUTES",
    "RESEND_MIN_INTERVAL_MINUTES",
    "utcnow",
    "hash_token",
    "verify_token",
    "split_public_token",
    "resolve_lifetime_minutes",
    "get_latest_token_for_user",
    "get_resend_min_interval_minutes",
    "get_resend_min_interval_seconds",
]
