# backend/services/email/types.py
from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel, EmailStr


class EmailRecipient(BaseModel):
    """收件人結構，未來若要擴充姓名欄位比較容易。"""
    email: EmailStr


class EmailMessage(BaseModel):
    """寄信請求物件，統一進入點，方便之後做 logging / queue 等擴充。"""
    to: Sequence[EmailRecipient]
    subject: str
    html: str
    cc: Sequence[EmailRecipient] | None = None
    bcc: Sequence[EmailRecipient] | None = None
    reply_to: EmailStr | None = None
