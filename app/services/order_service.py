from datetime import date

from app.exceptions import ApplicationError
from app.models import DashboardStats, OrderReceipt, OrderRequest, OrderSummary
from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.pc_build_repository import PcBuildRepository


class OrderService:
    COMPONENT_NAMES = ("GPU", "CPU", "Motherboard", "RAM", "PSU", "PC_Case")
    PAYMENT_STATUSES = ("Сплачено", "Не сплачено")
    ORDER_STATUSES = ("Готово", "Не готово")
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

    def list_orders(self) -> list[OrderSummary]:
        orders = []
        for row in self.order_repository.list_all():
            client = self.client_repository.get_by_id(int(row[1]))
            build = self.pc_build_repository.get_by_id(int(row[2]))
            build_label = "—"
            if build is not None:
                gpu = self.component_repository.get_by_id("GPU", int(build[1]))
                gpu_name = gpu[3] if gpu else "GPU"
                build_label = f"{build[8]} · {gpu_name}"
            orders.append(
                OrderSummary(
                    order_id=int(row[0]),
                    client_name=client[1] if client else "—",
                    build_label=build_label,
                    order_date=str(row[4]),
                    production_time=int(row[3]),
                    payment_status=str(row[5]),
                    due_amount=float(row[6]),
                    order_status=str(row[7]),
                )
            )
        return orders

    def build_dashboard_stats(self, clients_count: int, builds_count: int) -> DashboardStats:
        orders = self.list_orders()
        unpaid_count = sum(1 for order in orders if order.payment_status == self.UNPAID_STATUS)
        return DashboardStats(
            orders_count=len(orders),
            clients_count=clients_count,
            builds_count=builds_count,
            unpaid_count=unpaid_count,
        )

    def create_order(self, order_request: OrderRequest) -> OrderReceipt:
        if self.client_repository.get_by_id(order_request.client_id) is None:
            raise ApplicationError("Клієнта не знайдено. Зареєструйте клієнта та повторіть спробу.")

        total_price = self.pc_build_repository.get_total_price(order_request.pc_build_id)
        if total_price is None:
            raise ApplicationError("Збірку ПК з таким ID не знайдено.")

        if order_request.production_time < 1:
            raise ApplicationError("Час зборки має бути більшим за нуль.")
        if order_request.payment_status not in self.PAYMENT_STATUSES:
            raise ApplicationError("Оберіть коректний статус оплати.")
        if order_request.order_status not in self.ORDER_STATUSES:
            raise ApplicationError("Оберіть коректний статус замовлення.")

        due_amount = total_price if order_request.payment_status == self.UNPAID_STATUS else 0.0
        order_date = date.today()

        self.order_repository.create(
            client_id=order_request.client_id,
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
