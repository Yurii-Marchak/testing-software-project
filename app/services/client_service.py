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

    def update_client(self, client_id: int, registration: ClientRegistration) -> None:
        self.client_repository.update(
            client_id=client_id,
            full_name=registration.full_name,
            birth_date=registration.birth_date,
            email=registration.email,
            phone=registration.phone,
        )

    def delete_client(self, client_id: int) -> None:
        self.client_repository.delete(client_id)

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

    def get_client_form_values(self, client_id: int) -> dict[str, str] | None:
        client = self.get_client(client_id)
        if client is None:
            return None
        last_name, first_name = self._split_full_name(client.full_name)
        return {
            "client_id": str(client.client_id),
            "last_name": last_name,
            "first_name": first_name,
            "birth_date": client.birth_date,
            "email": client.email,
            "phone": client.phone,
        }

    def _to_summary(self, row: tuple) -> ClientSummary:
        return ClientSummary(
            client_id=int(row[0]),
            full_name=str(row[1]),
            birth_date=str(row[2]),
            email=str(row[3]),
            phone=str(row[4]),
        )

    def _split_full_name(self, full_name: str) -> tuple[str, str]:
        parts = full_name.split(" ", 1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]
