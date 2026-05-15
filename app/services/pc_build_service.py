from app.exceptions import ApplicationError
from app.models import PcBuildRequest
from app.repositories.component_repository import ComponentRepository
from app.repositories.pc_build_repository import PcBuildRepository


class PcBuildService:
    def __init__(
        self,
        component_repository: ComponentRepository,
        pc_build_repository: PcBuildRepository,
    ) -> None:
        self.component_repository = component_repository
        self.pc_build_repository = pc_build_repository

    def list_components(self, table_name: str) -> tuple[tuple, ...]:
        return self.component_repository.list_all(table_name)

    def create_build(self, build_request: PcBuildRequest) -> None:
        self._ensure_component_exists("GPU", build_request.gpu_id)
        self._ensure_component_exists("CPU", build_request.cpu_id)
        self._ensure_component_exists("Motherboard", build_request.motherboard_id)
        self._ensure_component_exists("RAM", build_request.ram_id)
        self._ensure_component_exists("PSU", build_request.psu_id)
        self._ensure_component_exists("PC_Case", build_request.pc_case_id)
        self.pc_build_repository.create(build_request)

    def _ensure_component_exists(self, table_name: str, component_id: int) -> None:
        if not self.component_repository.get_by_id(table_name, component_id):
            raise ApplicationError(f"Компонент у таблиці {table_name} з ID {component_id} не знайдено.")
