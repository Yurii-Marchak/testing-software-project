from pymysql.connections import Connection


class ClientRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, full_name: str, birth_date: str, email: str, phone: str) -> None:
        query = """
            INSERT INTO clients (full_name, birth_date, email, phone)
            VALUES (%s, %s, %s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (full_name, birth_date, email, phone))
        self.connection.commit()

    def get_id_by_name_and_phone(self, full_name: str, phone: str) -> int | None:
        query = "SELECT id FROM clients WHERE full_name = %s AND phone = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(query, (full_name, phone))
            client = cursor.fetchone()
        return client[0] if client else None
