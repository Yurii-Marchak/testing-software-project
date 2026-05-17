import os
import secrets
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str


def load_database_config() -> DatabaseConfig:
    _load_dotenv()

    password = _normalize_env_value(os.getenv("DB_PASSWORD", ""))
    if not password:
        raise ValueError(
            "Не задано пароль до бази даних. Вкажіть DB_PASSWORD у змінних оточення або у файлі .env."
        )

    return DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=password,
        database=os.getenv("DB_NAME", "lab7"),
    )


def load_app_secret_key() -> str:
    _load_dotenv()
    configured_secret = _normalize_env_value(os.getenv("APP_SECRET_KEY", ""))
    if configured_secret:
        return configured_secret
    return secrets.token_urlsafe(32)


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), _normalize_env_value(value))


def _normalize_env_value(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
