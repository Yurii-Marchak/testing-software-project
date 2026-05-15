from datetime import date

from app.exceptions import ApplicationError
from app.models import OrderReceipt, OrderRequest
from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.pc_build_repository import PcBuildRepository


class OrderService:
    COMPONENT_NAMES = ("GPU", "CPU", "Motherboard", "RAM", "PSU", "PC_Case")
    UNPAID_STATUS = "Не сплачено"

    def __init__(
        self,
        client_repository: ClientRepository,
        component_repository: ComponentRepository,
        pc_build_repository: PcBuildRepository,
        order_repository: OrderRepository,
    ) -> None:
        self.client_repository = client_repository
        self.component_repository = component_repository
        self.pc_build_repository = pc_build_repository
        self.order_repository = order_repository

    def list_builds(self) -> tuple[tuple, ...]:
        return self.pc_build_repository.list_all()

    def create_order(self, order_request: OrderRequest) -> OrderReceipt:
        client_id = self.client_repository.get_id_by_name_and_phone(
            order_request.client_name,
            order_request.client_phone,
        )
        if client_id is None:
            raise ApplicationError("Клієнта не знайдено. Спочатку зареєструйте його.")

        total_price = self.pc_build_repository.get_total_price(order_request.pc_build_id)
        if total_price is None:
            raise ApplicationError("Збірку ПК з таким ID не знайдено.")

        due_amount = total_price if order_request.payment_status == self.UNPAID_STATUS else 0.0
        order_date = date.today()

        self.order_repository.create(
            client_id=client_id,
            pc_build_id=order_request.pc_build_id,
            production_time=order_request.production_time,
            order_date=order_date,
            payment_status=order_request.payment_status,
            due_amount=due_amount,
            order_status=order_request.order_status,
        )

        component_summary = self.pc_build_repository.get_component_summary(order_request.pc_build_id)
        if component_summary is None:
            raise ApplicationError("Не вдалося сформувати чек для цієї збірки.")

        components = []
        for table_name, component_id in zip(self.COMPONENT_NAMES, component_summary[:-1]):
            component = self.component_repository.get_by_id(table_name, component_id)
            if component is None:
                raise ApplicationError(f"Не знайдено компонент {table_name} з ID {component_id}.")
            components.append((table_name, component[1:]))

        return OrderReceipt(
            order_date=order_date,
            due_amount=due_amount,
            total_price=float(component_summary[-1]),
            components=components,
        )
