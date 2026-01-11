# backend/core/static_site.py
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def mount_static_site(app: FastAPI) -> None:
    """
    掛載前端靜態網站到根路徑 '/'。

    注意：請在 include_router 之後呼叫，避免 root mount 吃掉其他路由。
    StaticFiles(html=True) 會在目錄請求時自動回傳 index.html。
    """
    backend_dir = Path(__file__).resolve().parents[1]  # .../backend
    project_root = backend_dir.parent                  # 專案根目錄
    static_dir = project_root / "web"

    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="site")
