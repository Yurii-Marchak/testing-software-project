from app.config import load_database_config
from app.infrastructure.database import create_connection
from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.pc_build_repository import PcBuildRepository
from app.services.client_service import ClientService
from app.services.order_service import OrderService
from app.services.pc_build_service import PcBuildService
from app.ui.console_app import ConsoleApp


def main() -> None:
    try:
        database_config = load_database_config()
    except ValueError as error:
        print(error)
        return

    connection = create_connection(database_config)
    if connection is None:
        return

    try:
        client_repository = ClientRepository(connection)
        component_repository = ComponentRepository(connection)
        pc_build_repository = PcBuildRepository(connection)
        order_repository = OrderRepository(connection)

        client_service = ClientService(client_repository)
        pc_build_service = PcBuildService(component_repository, pc_build_repository)
        order_service = OrderService(
            client_repository,
            component_repository,
            pc_build_repository,
            order_repository,
        )

        app = ConsoleApp(client_service, pc_build_service, order_service)
        app.run()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
