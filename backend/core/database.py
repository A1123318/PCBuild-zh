# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.settings import get_settings

DATABASE_URL = get_settings().database_url

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
