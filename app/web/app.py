from __future__ import annotations

from flask import Flask, request

from app.config import DatabaseConfig, load_app_secret_key
from app.web.controllers import register_routes
from app.web.runtime import close_request_scope, open_request_scope


def create_web_app(config: DatabaseConfig) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["DATABASE_CONFIG"] = config
    app.config["SECRET_KEY"] = load_app_secret_key()
    app.config["JSON_AS_ASCII"] = False

    @app.before_request
    def before_request() -> None:
        open_request_scope()

    @app.teardown_request
    def teardown_request(exception: BaseException | None) -> None:
        close_request_scope()

    @app.context_processor
    def inject_navigation() -> dict[str, str]:
        return {"current_path": request.path}

    register_routes(app)
    return app
