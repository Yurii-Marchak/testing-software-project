from dataclasses import dataclass

from pymysql.connections import Connection

from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.pc_build_repository import PcBuildRepository
from app.services.client_service import ClientService
from app.services.order_service import OrderService
from app.services.pc_build_service import PcBuildService


@dataclass
class ServiceContainer:
    client_service: ClientService
    pc_build_service: PcBuildService
    order_service: OrderService


def build_services(connection: Connection) -> ServiceContainer:
    client_repository = ClientRepository(connection)
    component_repository = ComponentRepository(connection)
    pc_build_repository = PcBuildRepository(connection)
    order_repository = OrderRepository(connection)

    return ServiceContainer(
        client_service=ClientService(client_repository),
        pc_build_service=PcBuildService(component_repository, pc_build_repository),
        order_service=OrderService(
            client_repository,
            component_repository,
            pc_build_repository,
            order_repository,
        ),
    )
