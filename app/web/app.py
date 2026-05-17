from __future__ import annotations

import secrets

from flask import Flask, abort, request, session

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
    app.config.setdefault("CSRF_ENABLED", True)

    @app.before_request
    def before_request() -> None:
        if request.method == "POST" and app.config.get("CSRF_ENABLED", True):
            _validate_csrf_token()
        if request.endpoint is None or request.endpoint == "static" or request.endpoint.startswith("debug_"):
            return
        open_request_scope()

    @app.teardown_request
    def teardown_request(exception: BaseException | None) -> None:
        close_request_scope()

    @app.context_processor
    def inject_navigation() -> dict[str, str]:
        return {"current_path": request.path, "csrf_token": _get_or_create_csrf_token()}

    @app.errorhandler(400)
    def bad_request(error) -> tuple[str, int]:
        return render_error_page(
            "400 | PC Build Manager",
            "400",
            "Некоректний запит",
            "Сервер не зміг обробити цей запит. Спробуйте оновити сторінку та повторити дію ще раз.",
            accent="amber",
            eyebrow="Request Rejected",
            details=(
                "Форма могла бути відправлена без службового токена безпеки або з невалідними даними.",
                "Оновіть сторінку, відкрийте форму повторно й спробуйте ще раз.",
            ),
        ), 400

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


def _get_or_create_csrf_token() -> str:
    csrf_token = session.get("_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["_csrf_token"] = csrf_token
    return csrf_token


def _validate_csrf_token() -> None:
    form_token = request.form.get("csrf_token", "")
    session_token = session.get("_csrf_token", "")
    if not form_token or not session_token or not secrets.compare_digest(form_token, session_token):
        abort(400)
