from app.exceptions import ApplicationError
from app.models import BuildSummary, ComponentOption, PcBuildRequest
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

    def list_component_options(self, table_name: str) -> list[ComponentOption]:
        return [self._to_component_option(table_name, row) for row in self.list_components(table_name)]

    def list_builds(self) -> list[BuildSummary]:
        builds = []
        for row in self.pc_build_repository.list_all():
            gpu = self.component_repository.get_by_id("GPU", int(row[1]))
            cpu = self.component_repository.get_by_id("CPU", int(row[2]))
            motherboard = self.component_repository.get_by_id("Motherboard", int(row[3]))
            ram = self.component_repository.get_by_id("RAM", int(row[4]))
            psu = self.component_repository.get_by_id("PSU", int(row[5]))
            pc_case = self.component_repository.get_by_id("PC_Case", int(row[6]))
            total_price = float(row[7] or 0)
            build_type = str(row[8])

            summary = BuildSummary(
                build_id=int(row[0]),
                build_type=build_type,
                gpu_name=gpu[1] if gpu else "—",
                cpu_name=cpu[1] if cpu else "—",
                motherboard_name=motherboard[1] if motherboard else "—",
                ram_name=ram[1] if ram else "—",
                psu_name=psu[1] if psu else "—",
                pc_case_name=pc_case[1] if pc_case else "—",
                total_price=total_price,
                label=f"#{row[0]} | {build_type} | {total_price:.2f} грн",
            )
            builds.append(summary)
        return builds

    def create_build(self, build_request: PcBuildRequest) -> None:
        if not build_request.build_type.strip():
            raise ApplicationError("Вкажіть тип збірки.")
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

    def _to_component_option(self, table_name: str, row: tuple) -> ComponentOption:
        details = " | ".join(str(value) for value in row[1:])
        return ComponentOption(
            component_id=int(row[0]),
            label=f"#{row[0]} | {table_name}: {details}",
        )
