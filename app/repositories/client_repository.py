from pymysql.connections import Connection


class ClientRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, full_name: str, birth_date: str, email: str, phone: str) -> int:
        query = """
            INSERT INTO clients (full_name, birth_date, email, phone)
            VALUES (%s, %s, %s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (full_name, birth_date, email, phone))
            client_id = cursor.lastrowid
        self.connection.commit()
        return client_id

    def get_by_id(self, client_id: int) -> tuple | None:
        query = "SELECT id, full_name, birth_date, email, phone FROM clients WHERE id = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(query, (client_id,))
            return cursor.fetchone()

    def update(self, client_id: int, full_name: str, birth_date: str, email: str, phone: str) -> None:
        query = """
            UPDATE clients
            SET full_name = %s, birth_date = %s, email = %s, phone = %s
            WHERE id = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (full_name, birth_date, email, phone, client_id))
        self.connection.commit()

    def delete(self, client_id: int) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        self.connection.commit()

    def list_all(self) -> tuple[tuple, ...]:
        query = "SELECT id, full_name, birth_date, email, phone FROM clients ORDER BY full_name"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def find_by_phone(self, phone: str) -> tuple[tuple, ...]:
        query = """
            SELECT id, full_name, birth_date, email, phone
            FROM clients
            WHERE phone LIKE %s
            ORDER BY full_name
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (f"%{phone}%",))
            return cursor.fetchall()
