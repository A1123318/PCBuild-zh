# backend/core/security_headers.py
from __future__ import annotations

from fastapi import FastAPI, Request
from starlette.responses import Response


def add_security_headers_middleware(app: FastAPI) -> None:
    """
    依 OWASP Security Headers 建議，為所有回應加上基礎安全標頭。
    目前刻意不加入 CSP（你有大量 inline script 時容易破壞前端行為）。
    """
    @app.middleware("http")
    async def _security_headers(request: Request, call_next):
        response: Response = await call_next(request)

        # X-Content-Type-Options: 防止 MIME sniffing
        if "x-content-type-options" not in response.headers:
            response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer-Policy: 降低跨站 referrer 洩漏
        if "referrer-policy" not in response.headers:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # X-Frame-Options: 防止 clickjacking（對 JSON API 影響不大，但對頁面有效）
        if "x-frame-options" not in response.headers:
            response.headers["X-Frame-Options"] = "DENY"

        # Permissions-Policy: 關閉你不需要的瀏覽器特性（可依需求調整）
        if "permissions-policy" not in response.headers:
            response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        # HSTS: 告知瀏覽器只用 HTTPS 存取（你走 Cloudflare HTTPS 對外，適用）
        # 先用較保守版本（不加 includeSubDomains/preload），避免誤設造成子網域被鎖死
        if "strict-transport-security" not in response.headers:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"

        return response
