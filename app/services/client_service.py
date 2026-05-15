from app.models import ClientRegistration, ClientSummary
from app.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, client_repository: ClientRepository) -> None:
        self.client_repository = client_repository

    def register_client(self, registration: ClientRegistration) -> int:
        return self.client_repository.create(
            full_name=registration.full_name,
            birth_date=registration.birth_date,
            email=registration.email,
            phone=registration.phone,
        )

    def list_clients(self, phone_query: str = "") -> list[ClientSummary]:
        rows = (
            self.client_repository.find_by_phone(phone_query)
            if phone_query
            else self.client_repository.list_all()
        )
        return [self._to_summary(row) for row in rows]

    def get_client(self, client_id: int) -> ClientSummary | None:
        row = self.client_repository.get_by_id(client_id)
        if row is None:
            return None
        return self._to_summary(row)

    def _to_summary(self, row: tuple) -> ClientSummary:
        return ClientSummary(
            client_id=int(row[0]),
            full_name=str(row[1]),
            birth_date=str(row[2]),
            email=str(row[3]),
            phone=str(row[4]),
        )
