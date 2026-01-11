# backend/core/app_factory.py
from fastapi import FastAPI

from backend.core.cors import add_cors_middleware
from backend.core.docs_gate import DocsGateMiddleware
from backend.core.routes import include_api_routes
from backend.core.static_site import mount_static_site


def create_app() -> FastAPI:
    """
    Application factory：集中管理 app 組裝順序，避免在 import 時散落初始化邏輯。
    """
    app = FastAPI()

    add_cors_middleware(app)
    app.add_middleware(DocsGateMiddleware)

    # 先掛 API，再掛根路徑的靜態站（避免 "/" mount 影響其他路由）
    include_api_routes(app)
    mount_static_site(app)

    return app
