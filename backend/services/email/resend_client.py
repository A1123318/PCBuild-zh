# backend/services/email/resend_client.py
from __future__ import annotations

import resend

from .config import get_resend_settings
from .types import EmailMessage


class ResendEmailClient:
    """封裝 Resend SDK。"""

    def __init__(self) -> None:
        settings = get_resend_settings()
        resend.api_key = settings.api_key
        self._from_header = settings.from_header

    def send_email(self, message: EmailMessage) -> str:
        """送出 Email，回傳 Resend 產生的 email id。"""
        to_list = [r.email for r in message.to]
        cc_list = [r.email for r in (message.cc or [])] or None
        bcc_list = [r.email for r in (message.bcc or [])] or None

        payload: dict = {
            "from": self._from_header,
            "to": to_list,
            "subject": message.subject,
            "html": message.html,
        }
        if cc_list:
            payload["cc"] = cc_list
        if bcc_list:
            payload["bcc"] = bcc_list
        if message.reply_to:
            payload["reply_to"] = message.reply_to

        result = resend.Emails.send(payload)

        email_id = getattr(result, "id", None)
        if email_id is None and isinstance(result, dict):
            email_id = result.get("id")

        if not email_id:
            raise RuntimeError("Resend did not return an email id.")

        return str(email_id)
