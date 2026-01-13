# backend/services/auth/verification/repo.py
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import EmailVerificationToken
from backend.services.auth.verification.types import VerificationPurpose


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


def get_resend_min_interval_minutes(purpose: VerificationPurpose) -> int:
    return RESEND_MIN_INTERVAL_MINUTES[purpose]


def get_resend_min_interval_seconds(purpose: VerificationPurpose) -> int:
    return get_resend_min_interval_minutes(purpose) * 60
