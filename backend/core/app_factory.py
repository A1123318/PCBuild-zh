# backend/core/app_factory.py
from fastapi import FastAPI

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.core.cors import add_cors_middleware
from backend.core.docs_gate import DocsGateMiddleware
from backend.core.rate_limit import limiter
from backend.core.routes import include_api_routes
from backend.core.settings import get_settings
from backend.core.static_site import mount_static_site


def create_app() -> FastAPI:
    app = FastAPI()
    settings = get_settings()

    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

    add_cors_middleware(app)
    app.add_middleware(DocsGateMiddleware)

    include_api_routes(app)
    mount_static_site(app)
    return app
