from pymysql.connections import Connection


class ComponentRepository:
    ALLOWED_TABLES = (
        "GPU",
        "CPU",
        "Motherboard",
        "RAM",
        "PSU",
        "PC_Case",
    )

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def list_all(self, table_name: str) -> tuple[tuple, ...]:
        self._validate_table_name(table_name)
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

    def get_by_id(self, table_name: str, component_id: int) -> tuple | None:
        self._validate_table_name(table_name)
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (component_id,))
            return cursor.fetchone()

    def _validate_table_name(self, table_name: str) -> None:
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Unsupported component table: {table_name}")
