# backend/api/dependencies/db.py
from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    提供 FastAPI Depends 使用的資料庫 Session。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
