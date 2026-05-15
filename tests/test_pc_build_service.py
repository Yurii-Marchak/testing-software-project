import pytest

from app.exceptions import ApplicationError
from app.models import PcBuildRequest
from app.services.pc_build_service import PcBuildService


class FakeComponentRepository:
    def __init__(self, components):
        self.components = components

    def list_all(self, table_name):
        return tuple(row for (current_table, _), row in self.components.items() if current_table == table_name)

    def get_by_id(self, table_name, component_id):
        return self.components.get((table_name, component_id))


class FakePcBuildRepository:
    def __init__(self):
        self.created = []
        self.rows = []

    def create(self, build_request):
        self.created.append(build_request)

    def list_all(self):
        return tuple(self.rows)


def build_service():
    components = {
        ("GPU", 1): (1, "RTX 4060"),
        ("CPU", 2): (2, "Ryzen 5 7600"),
        ("Motherboard", 3): (3, "B650M"),
        ("RAM", 4): (4, "DDR5 32GB"),
        ("PSU", 5): (5, "750W Gold"),
        ("PC_Case", 6): (6, "Corsair 4000D"),
    }
    repository = FakePcBuildRepository()
    service = PcBuildService(FakeComponentRepository(components), repository)
    return service, repository


def test_create_build_persists_valid_configuration():
    service, repository = build_service()
    request = PcBuildRequest(1, 2, 3, 4, 5, 6, "Ігрова")

    service.create_build(request)

    assert repository.created == [request]


def test_create_build_rejects_missing_component():
    service, _ = build_service()
    request = PcBuildRequest(99, 2, 3, 4, 5, 6, "Ігрова")

    with pytest.raises(ApplicationError, match="не знайдено"):
        service.create_build(request)
