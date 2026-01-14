# backend/core/rate_limit.py
from __future__ import annotations

from fastapi import Request
from slowapi import Limiter

from backend.core.settings import get_settings


def _get_client_ip(request: Request) -> str:
    """
    Cloudflare Tunnel / Proxy 情境下，request.client.host 可能是內網 IP，
    因此優先使用 Cloudflare 帶來的原始訪客 IP。
    """
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()

    xff = request.headers.get("X-Forwarded-For")
    if xff:
        # 可能是 "client, proxy1, proxy2"；取第一個
        return xff.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


_settings = get_settings()

limiter = Limiter(
    key_func=_get_client_ip,
    default_limits=[_settings.rate_limit_default],
    enabled=_settings.rate_limit_enabled,
    headers_enabled=True,
)
