# backend/core/middleware/throttling/rate_limit.py
from __future__ import annotations

from ipaddress import ip_address  # ← 新增
from fastapi import Request
from slowapi import Limiter

from backend.core.settings import get_settings


def _clean_ip(value: str | None) -> str | None:  # ← 新增
    if not value:
        return None
    value = value.strip()
    try:
        return str(ip_address(value))
    except ValueError:
        return None


def _get_client_ip(request: Request) -> str:
    """
    僅信任 Cloudflare 帶來的 CF-Connecting-IP（前提：流量確實經 Cloudflare edge 到 origin）。
    不信任 X-Forwarded-For（可被客戶端偽造）。
    """
    cf_ip = _clean_ip(request.headers.get("CF-Connecting-IP"))
    if cf_ip:
        return cf_ip

    if request.client and request.client.host:
        host = request.client.host.strip()
        try:
            return str(ip_address(host))
        except ValueError:
            # host 理論上來自 socket peer，仍可保留原值
            return host

    return "127.0.0.1"


_settings = get_settings()

limiter = Limiter(
    key_func=_get_client_ip,
    default_limits=[_settings.rate_limit_default],
    enabled=_settings.rate_limit_enabled,
    headers_enabled=True,  # ← 保留你原本行為（若你想關可再談）
    storage_uri=_settings.rate_limit_storage_uri,

    # 新增：Redis 暫時不可用時，退回 memory（避免服務整體失效）
    in_memory_fallback_enabled=True,
    in_memory_fallback=[_settings.rate_limit_default],

    # 新增：避免同一個 Redis 被其他專案共用時 key 衝突（你有多個 compose 專案時特別有用）
    key_prefix="pcbuild:",
)
