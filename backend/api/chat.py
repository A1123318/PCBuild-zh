# backend/api/chat.py
from fastapi import APIRouter, Depends

from backend.api.auth_deps import get_active_user
from backend.models import User
from backend.schemas.chat import ChatIn, ChatOut
from backend.services.chat.service import generate_chat_reply

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatOut)
def chat(
    body: ChatIn,
    _: User = Depends(get_active_user),  # 未登入→401；未驗證→403
) -> ChatOut:
    reply_text = generate_chat_reply(message=body.message, history=body.history)
    return ChatOut(reply=reply_text)
