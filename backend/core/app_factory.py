# backend/core/app_factory.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.core.cors import add_cors_middleware
from backend.core.docs_gate import DocsGateMiddleware
from backend.core.rate_limit import limiter
from backend.core.routes import include_api_routes
from backend.core.settings import get_settings
from backend.core.static_site import mount_static_site
from backend.core.rate_limit_handler import rate_limit_exceeded_handler
from backend.core.security_headers import add_security_headers_middleware
from backend.core.csrf import add_csrf_protection_middleware
from backend.core.debug_gate import add_debug_gate_middleware


def create_app() -> FastAPI:
    app = FastAPI()
    settings = get_settings()

    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

    add_cors_middleware(app)
    add_csrf_protection_middleware(app)
    add_security_headers_middleware(app)
    add_debug_gate_middleware(app)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "pcbuild.redfiretw.xyz",
            "localhost",
            "127.0.0.1",
        ],
    )

    include_api_routes(app)
    mount_static_site(app)
    return app
