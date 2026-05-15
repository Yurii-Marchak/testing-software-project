from __future__ import annotations

from app.web.rendering import page_renderer
from app.web.runtime import services


def register_component_routes(app) -> None:
    @app.get("/components", endpoint="components")
    def components() -> str:
        return page_renderer(services()).render_components()
