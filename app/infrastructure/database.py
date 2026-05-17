import pymysql
from pymysql.connections import Connection
from pymysql.err import MySQLError

from app.config import DatabaseConfig


def create_connection(config: DatabaseConfig) -> Connection | None:
    try:
        return pymysql.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=config.database,
            charset="utf8mb4",
        )
    except MySQLError as error:
        print("Помилка підключення до бази даних:", error)
        return None
