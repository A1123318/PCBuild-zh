# backend/api/auth_config.py
import os
from pydantic import EmailStr, TypeAdapter

EMAIL_ADAPTER = TypeAdapter(EmailStr)

SESSION_COOKIE_NAME = "pcbuild_session"
SESSION_EXPIRES_MINUTES = int(os.getenv("SESSION_EXPIRES_MINUTES", "120"))

from backend.services.auth.verification.core import (
    VerificationPurpose,
    get_resend_min_interval_seconds,
)

RESEND_SIGNUP_MIN_INTERVAL_SECONDS = get_resend_min_interval_seconds(VerificationPurpose.SIGNUP)
RESEND_PASSWORD_RESET_MIN_INTERVAL_SECONDS = get_resend_min_interval_seconds(VerificationPurpose.PASSWORD_RESET)
