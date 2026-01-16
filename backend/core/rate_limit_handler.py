# backend/core/rate_limit_handler.py
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    統一 429 回應格式為專案既有的 {"errors": {...}}。
    同時保留 SlowAPI 預設 handler 產生的 headers（例如 Retry-After、X-RateLimit-*）。
    """
    default_resp = _rate_limit_exceeded_handler(request, exc)

    payload = {"errors": {"_global": "請求過於頻繁，請稍後再試。"}}
    resp = JSONResponse(status_code=429, content=payload)

    # 保留 SlowAPI 預設回應的 header（Retry-After / X-RateLimit-* 等）
    for k, v in default_resp.headers.items():
        resp.headers[k] = v

    return resp
