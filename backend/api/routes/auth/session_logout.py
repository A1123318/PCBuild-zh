# backend/api/routes/auth/session_logout.py
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session as OrmSession

from backend.api.deps import get_db
from backend.api.auth_config import SESSION_COOKIE_NAME
from backend.api.auth_utils import clear_session_cookie
from backend.models import Session as SessionModel

router = APIRouter()


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    db: OrmSession = Depends(get_db),
):
    """
    將目前 session 標記為 revoked，並清除瀏覽器 Cookie。
    未登入時呼叫也回 204，不暴露細節。
    """
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)

    if raw_token:
        try:
            session_id = UUID(raw_token)
            session = (
                db.query(SessionModel)
                .filter(SessionModel.id == session_id, SessionModel.revoked.is_(False))
                .first()
            )
            if session:
                session.revoked = True
                db.commit()
        except ValueError:
            # Cookie 不是合法 UUID，忽略即可
            pass

    clear_session_cookie(response)
    return
