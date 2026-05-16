from pymysql.connections import Connection


class ComponentRepository:
    TABLE_FIELDS = {
        "GPU": (
            "model_name",
            "manufacturer",
            "gpu_name",
            "video_memory",
            "memory_type",
            "fan_count",
            "power_consumption",
            "recommended_psu_power",
            "price",
        ),
        "CPU": (
            "model_name",
            "manufacturer",
            "tdp",
            "cores",
            "threads",
            "process_nm",
            "base_clock",
            "turbo_clock",
            "compatible_ram_type",
            "price",
        ),
        "Motherboard": (
            "model_name",
            "manufacturer",
            "socket",
            "chipset",
            "ram_slots",
            "max_ram_frequency",
            "form_factor",
            "ram_type",
            "price",
        ),
        "RAM": (
            "model_name",
            "manufacturer",
            "capacity",
            "frequency",
            "ram_type",
            "kit_count",
            "price",
        ),
        "PSU": (
            "model_name",
            "manufacturer",
            "power",
            "certificate",
            "form_factor",
            "modularity",
            "price",
        ),
        "PC_Case": (
            "model_name",
            "manufacturer",
            "form_factor",
            "glass_side_panel",
            "included_fans",
            "price",
        ),
    }
    ALLOWED_TABLES = tuple(TABLE_FIELDS.keys())

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

    def create(self, table_name: str, values: dict[str, object]) -> None:
        self._validate_table_name(table_name)
        fields = self._validated_fields(table_name, values)
        placeholders = ", ".join(["%s"] * len(fields))
        columns = ", ".join(fields)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        params = tuple(values[field] for field in fields)
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
        self.connection.commit()

    def update(self, table_name: str, component_id: int, values: dict[str, object]) -> None:
        self._validate_table_name(table_name)
        fields = self._validated_fields(table_name, values)
        assignments = ", ".join(f"{field} = %s" for field in fields)
        query = f"UPDATE {table_name} SET {assignments} WHERE id = %s"
        params = tuple(values[field] for field in fields) + (component_id,)
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
        self.connection.commit()

    def delete(self, table_name: str, component_id: int) -> None:
        self._validate_table_name(table_name)
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (component_id,))
        self.connection.commit()

    def _validate_table_name(self, table_name: str) -> None:
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Unsupported component table: {table_name}")

    def _validated_fields(self, table_name: str, values: dict[str, object]) -> tuple[str, ...]:
        allowed_fields = self.TABLE_FIELDS[table_name]
        provided_fields = tuple(field for field in allowed_fields if field in values)
        if len(provided_fields) != len(allowed_fields):
            missing = set(allowed_fields) - set(provided_fields)
            raise ValueError(f"Missing fields for {table_name}: {', '.join(sorted(missing))}")
        return provided_fields
