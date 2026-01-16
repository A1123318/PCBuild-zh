# backend/core/debug_gate.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.core.settings import get_settings


def add_debug_gate_middleware(app: FastAPI) -> None:
    settings = get_settings()

    @app.middleware("http")
    async def _debug_gate(request: Request, call_next):
        # 預設關閉 /debug/*（避免公開環境資訊洩漏）
        if request.url.path.startswith("/debug") and not settings.debug_routes_enabled:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        return await call_next(request)
