from datetime import date

from pymysql.connections import Connection


class OrderRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(
        self,
        client_id: int,
        pc_build_id: int,
        production_time: int,
        order_date: date,
        payment_status: str,
        due_amount: float,
        order_status: str,
    ) -> None:
        query = """
            INSERT INTO order_journal (
                client_id, pc_build_id, production_time, order_date,
                payment_status, due_amount, order_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            client_id,
            pc_build_id,
            production_time,
            order_date,
            payment_status,
            due_amount,
            order_status,
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
        self.connection.commit()

    def list_all(self) -> tuple[tuple, ...]:
        query = """
            SELECT id, client_id, pc_build_id, production_time, order_date, payment_status, due_amount, order_status
            FROM order_journal
            ORDER BY order_date DESC, id DESC
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
