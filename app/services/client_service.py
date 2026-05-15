from app.models import ClientRegistration
from app.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, client_repository: ClientRepository) -> None:
        self.client_repository = client_repository

    def register_client(self, registration: ClientRegistration) -> None:
        self.client_repository.create(
            full_name=registration.full_name,
            birth_date=registration.birth_date,
            email=registration.email,
            phone=registration.phone,
        )
