import os

from app.config import load_database_config
from app.web.app import create_web_app


def main() -> None:
    try:
        database_config = load_database_config()
    except ValueError as error:
        print(error)
        return

    app = create_web_app(database_config)
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )


if __name__ == "__main__":
    main()
