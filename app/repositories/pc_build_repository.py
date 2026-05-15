from pymysql.connections import Connection

from app.models import PcBuildRequest


class PcBuildRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, build_request: PcBuildRequest) -> None:
        query = """
            INSERT INTO PC_Build (
                gpu_id, cpu_id, motherboard_id, ram_id, psu_id, pc_case_id, build_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            build_request.gpu_id,
            build_request.cpu_id,
            build_request.motherboard_id,
            build_request.ram_id,
            build_request.psu_id,
            build_request.pc_case_id,
            build_request.build_type,
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
        self.connection.commit()

    def list_all(self) -> tuple[tuple, ...]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM PC_Build")
            return cursor.fetchall()

    def get_by_id(self, build_id: int) -> tuple | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM PC_Build WHERE id = %s", (build_id,))
            return cursor.fetchone()

    def get_total_price(self, build_id: int) -> float | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT total_price FROM PC_Build WHERE id = %s", (build_id,))
            result = cursor.fetchone()
        return float(result[0]) if result else None

    def get_component_summary(self, build_id: int) -> tuple | None:
        query = """
            SELECT gpu_id, cpu_id, motherboard_id, ram_id, psu_id, pc_case_id, total_price
            FROM PC_Build WHERE id = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (build_id,))
            return cursor.fetchone()
