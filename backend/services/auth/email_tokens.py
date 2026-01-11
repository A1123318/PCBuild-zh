# backend/services/auth/email_tokens.py
from __future__ import annotations

import secrets
from datetime import timedelta

from sqlalchemy.orm import Session

from backend.models import User, EmailVerificationToken
from backend.services.auth.verification.core import (
    VerificationPurpose,
    RESEND_MIN_INTERVAL_MINUTES,
    VerificationEmailRateLimitedError,
    TokenState,
    InvalidOrExpiredTokenError,
    utcnow,
    hash_token,
    verify_token,
    split_public_token,
    resolve_lifetime_minutes,
    get_latest_token_for_user,
)


def issue_verification_token(
    db: Session,
    user: User,
    *,
    purpose: VerificationPurpose,
    expires_in_minutes: int | None = None,
) -> str:
    """
    發行驗證碼（通用版本）。
    回傳 public token 格式為 "<id>.<secret>"
    """
    lifetime_minutes = resolve_lifetime_minutes(purpose, expires_in_minutes)

    secret = secrets.token_urlsafe(32)
    token_hash = hash_token(secret)
    now = utcnow()
    expires_at = now + timedelta(minutes=lifetime_minutes)

    token = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        purpose=purpose.value,
        is_used=False,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    return f"{token.id}.{secret}"


def issue_password_reset_token_for_user(
    db: Session,
    user: User,
    *,
    min_interval_minutes: int | None = None,
) -> str:
    """
    忘記密碼流程專用：為指定使用者發行「重設密碼」 token。
    - 依 PASSWORD_RESET 冷卻時間做簡單 rate limit
    """
    now = utcnow()

    if min_interval_minutes is None:
        min_interval_minutes = RESEND_MIN_INTERVAL_MINUTES[
            VerificationPurpose.PASSWORD_RESET
        ]

    latest = get_latest_token_for_user(
        db=db,
        user_id=user.id,
        purpose=VerificationPurpose.PASSWORD_RESET,
    )
    if latest is not None and latest.created_at + timedelta(minutes=min_interval_minutes) > now:
        raise VerificationEmailRateLimitedError("重設密碼請求太頻繁，請稍後再試。")

    return issue_verification_token(
        db=db,
        user=user,
        purpose=VerificationPurpose.PASSWORD_RESET,
    )


def _load_valid_token_and_user(
    db: Session,
    public_token: str,
    *,
    expected_purpose: VerificationPurpose,
) -> tuple[EmailVerificationToken, User]:
    """
    依 public_token 載入並驗證 token + user，但「不改寫也不 commit」。
    """
    token_id, secret = split_public_token(public_token)

    token = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.id == token_id,
            EmailVerificationToken.purpose == expected_purpose.value,
        )
        .first()
    )
    if token is None:
        raise InvalidOrExpiredTokenError("找不到對應的驗證資訊。", state=TokenState.INVALID)

    user = db.query(User).filter(User.id == token.user_id).first()
    if user is None:
        raise InvalidOrExpiredTokenError("找不到對應的驗證資訊。", state=TokenState.INVALID)

    if not verify_token(secret, token.token_hash):
        raise InvalidOrExpiredTokenError("找不到對應的驗證資訊。", state=TokenState.INVALID)

    now = utcnow()
    if token.expires_at < now:
        raise InvalidOrExpiredTokenError(state=TokenState.EXPIRED)

    if expected_purpose == VerificationPurpose.PASSWORD_RESET:
        latest = get_latest_token_for_user(
            db=db,
            user_id=user.id,
            purpose=VerificationPurpose.PASSWORD_RESET,
        )
        if latest is not None and latest.id != token.id:
            raise InvalidOrExpiredTokenError(state=TokenState.SUPERSEDED)

        if token.is_used:
            raise InvalidOrExpiredTokenError(state=TokenState.USED)
    else:
        if token.is_used:
            raise InvalidOrExpiredTokenError(state=TokenState.USED)

        if expected_purpose == VerificationPurpose.SIGNUP and user.is_active:
            raise InvalidOrExpiredTokenError(state=TokenState.ALREADY_VERIFIED)

    return token, user


def load_valid_token_and_user(
    db: Session,
    public_token: str,
    *,
    expected_purpose: VerificationPurpose,
) -> tuple[EmailVerificationToken, User]:
    """
    公開的 read-only 驗證介面：只做載入與檢查，不改寫 token，也不 commit。
    """
    return _load_valid_token_and_user(
        db=db,
        public_token=public_token,
        expected_purpose=expected_purpose,
    )


def consume_verification_token(
    db: Session,
    public_token: str,
    *,
    purpose: VerificationPurpose,
) -> tuple[User, EmailVerificationToken]:
    """
    通用「消費 token」流程：
    - 驗證 token
    - 將 token.is_used 設為 True（不在這裡 commit）
    - 回傳 (user, token)，由呼叫端決定 transaction 邊界
    """
    token, user = _load_valid_token_and_user(
        db=db,
        public_token=public_token,
        expected_purpose=purpose,
    )
    token.is_used = True
    return user, token
