from __future__ import annotations

from app.web.rendering import page_renderer
from app.web.runtime import services


def register_dashboard_routes(app) -> None:
    @app.get("/", endpoint="home")
    def home() -> str:
        return page_renderer(services()).render_dashboard()
