from app.exceptions import ApplicationError
from app.models import BuildSummary, ComponentOption, PcBuildRequest
from app.repositories.component_repository import ComponentRepository
from app.repositories.pc_build_repository import PcBuildRepository


class PcBuildService:
    COMPONENT_TABLES = (
        ("GPU", "gpu_id"),
        ("CPU", "cpu_id"),
        ("Motherboard", "motherboard_id"),
        ("RAM", "ram_id"),
        ("PSU", "psu_id"),
        ("PC_Case", "pc_case_id"),
    )

    def __init__(
        self,
        component_repository: ComponentRepository,
        pc_build_repository: PcBuildRepository,
    ) -> None:
        self.component_repository = component_repository
        self.pc_build_repository = pc_build_repository

    def list_components(self, table_name: str) -> tuple[tuple, ...]:
        return self.component_repository.list_all(table_name)

    def list_component_options(self, table_name: str) -> list[ComponentOption]:
        return [self._to_component_option(table_name, row) for row in self.list_components(table_name)]

    def list_builds(self) -> list[BuildSummary]:
        return [self._to_build_summary(row) for row in self.pc_build_repository.list_all()]

    def create_build(self, build_request: PcBuildRequest) -> None:
        self._validate_build_request(build_request)
        self.pc_build_repository.create(build_request)

    def _to_build_summary(self, row: tuple) -> BuildSummary:
        component_names = {
            "gpu_name": self._component_name("GPU", int(row[1])),
            "cpu_name": self._component_name("CPU", int(row[2])),
            "motherboard_name": self._component_name("Motherboard", int(row[3])),
            "ram_name": self._component_name("RAM", int(row[4])),
            "psu_name": self._component_name("PSU", int(row[5])),
            "pc_case_name": self._component_name("PC_Case", int(row[6])),
        }
        total_price = float(row[7] or 0)
        build_type = str(row[8])
        return BuildSummary(
            build_id=int(row[0]),
            build_type=build_type,
            total_price=total_price,
            label=f"#{row[0]} | {build_type} | {total_price:.2f} грн",
            **component_names,
        )

    def _component_name(self, table_name: str, component_id: int) -> str:
        component = self.component_repository.get_by_id(table_name, component_id)
        return component[1] if component else "—"

    def _validate_build_request(self, build_request: PcBuildRequest) -> None:
        if not build_request.build_type.strip():
            raise ApplicationError("Вкажіть тип збірки.")
        for table_name, attribute_name in self.COMPONENT_TABLES:
            self._ensure_component_exists(table_name, getattr(build_request, attribute_name))

    def _ensure_component_exists(self, table_name: str, component_id: int) -> None:
        if not self.component_repository.get_by_id(table_name, component_id):
            raise ApplicationError(f"Компонент у таблиці {table_name} з ID {component_id} не знайдено.")

    def _to_component_option(self, table_name: str, row: tuple) -> ComponentOption:
        details = " | ".join(str(value) for value in row[1:])
        return ComponentOption(
            component_id=int(row[0]),
            label=f"#{row[0]} | {table_name}: {details}",
        )
