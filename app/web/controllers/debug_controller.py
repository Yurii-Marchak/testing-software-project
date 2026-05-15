from __future__ import annotations

from flask import abort


def register_debug_routes(app) -> None:
    @app.get("/error/404", endpoint="debug_error_404")
    def debug_error_404() -> None:
        abort(404)

    @app.get("/error/500", endpoint="debug_error_500")
    def debug_error_500() -> None:
        raise RuntimeError("Debug route triggered 500 error.")
