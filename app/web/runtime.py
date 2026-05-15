from __future__ import annotations

from flask import current_app, g

from app.config import DatabaseConfig
from app.infrastructure.database import create_connection
from app.web.dependencies import ServiceContainer, build_services


def open_request_scope() -> None:
    database_config: DatabaseConfig = current_app.config["DATABASE_CONFIG"]
    connection = create_connection(database_config)
    if connection is None:
        raise RuntimeError("Не вдалося підключитися до бази даних.")
    g.db_connection = connection
    g.services = build_services(connection)


def close_request_scope() -> None:
    connection = getattr(g, "db_connection", None)
    if connection is not None:
        connection.close()


def services() -> ServiceContainer:
    return g.services
