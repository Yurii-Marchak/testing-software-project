from __future__ import annotations

from flask import Flask, request

from app.config import DatabaseConfig, load_app_secret_key
from app.web.controllers import register_routes
from app.web.runtime import close_request_scope, open_request_scope
from app.web.rendering import render_error_page


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
        if request.endpoint is None or request.endpoint == "static" or request.endpoint.startswith("debug_"):
            return
        open_request_scope()

    @app.teardown_request
    def teardown_request(exception: BaseException | None) -> None:
        close_request_scope()

    @app.context_processor
    def inject_navigation() -> dict[str, str]:
        return {"current_path": request.path}

    @app.errorhandler(404)
    def not_found(error) -> tuple[str, int]:
        return render_error_page(
            "404 | PC Build Manager",
            "404",
            "Сторінку не знайдено",
            "Схоже, посилання застаріло або адреса була введена з помилкою. Поверніться на дашборд або відкрийте потрібний розділ із меню.",
            accent="cyan",
            eyebrow="Lost Route",
            details=(
                "Маршрут не існує в поточній конфігурації застосунку.",
                "Перевірте URL або скористайтеся навігацією зліва.",
            ),
        ), 404

    @app.errorhandler(500)
    def internal_server_error(error) -> tuple[str, int]:
        return render_error_page(
            "500 | PC Build Manager",
            "500",
            "Внутрішня помилка сервера",
            "Під час обробки запиту сталася непередбачена помилка. Спробуйте оновити сторінку або поверніться на головний екран.",
            accent="amber",
            eyebrow="System Fault",
            details=(
                "Сервіс отримав запит, але не зміг завершити його коректно.",
                "Якщо проблема повторюється, перевірте стан сервера та підключення до БД.",
            ),
        ), 500

    register_routes(app)
    return app
