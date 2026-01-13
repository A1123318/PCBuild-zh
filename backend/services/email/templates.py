# backend/services/email/templates.py
from __future__ import annotations

from .templates_password_reset import build_password_reset_email
from .templates_signup import build_signup_verification_email

__all__ = [
    "build_signup_verification_email",
    "build_password_reset_email",
]
