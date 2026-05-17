from datetime import date

from app.exceptions import ApplicationError
from app.models import DashboardStats, OrderReceipt, OrderRequest, OrderSummary
from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.pc_build_repository import PcBuildRepository


class OrderService:
    COMPONENT_NAMES = ("GPU", "CPU", "Motherboard", "RAM", "PSU", "PC_Case")
    PAYMENT_STATUSES = ("paid", "unpaid")
    ORDER_STATUSES = ("ready", "not_ready")
    PAYMENT_STATUS_LABELS = {
        "paid": "Сплачено",
        "unpaid": "Не сплачено",
    }
    ORDER_STATUS_LABELS = {
        "ready": "Готово",
        "not_ready": "Не готово",
    }
    UNPAID_STATUS = "unpaid"

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
        return [self._build_order_summary(row) for row in self.order_repository.list_all()]

    def get_order_form_values(self, order_id: int) -> dict[str, str] | None:
        row = self.order_repository.get_by_id(order_id)
        if row is None:
            return None
        return {
            "order_id": str(row[0]),
            "client_id": str(row[1]),
            "pc_build_id": str(row[2]),
            "production_time": str(row[3]),
            "order_date": str(row[4]),
            "payment_status": str(row[5]),
            "order_status": str(row[7]),
        }

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
        self._ensure_client_exists(order_request.client_id)
        total_price = self._get_total_price(order_request.pc_build_id)
        self._validate_order_request(order_request)
        due_amount = self._calculate_due_amount(total_price, order_request.payment_status)
        order_date = date.today()
        component_summary = self._get_component_summary(order_request.pc_build_id)
        receipt = self._build_receipt(order_date, due_amount, component_summary)
        self._persist_order_transactionally(order_request, order_date, due_amount)
        return receipt

    def update_order(self, order_id: int, order_request: OrderRequest) -> None:
        existing_order = self.order_repository.get_by_id(order_id)
        if existing_order is None:
            raise ApplicationError("Замовлення не знайдено.")
        self._ensure_client_exists(order_request.client_id)
        total_price = self._get_total_price(order_request.pc_build_id)
        self._validate_order_request(order_request)
        due_amount = self._calculate_due_amount(total_price, order_request.payment_status)
        self.order_repository.update(
            order_id=order_id,
            client_id=order_request.client_id,
            pc_build_id=order_request.pc_build_id,
            production_time=order_request.production_time,
            payment_status=order_request.payment_status,
            due_amount=due_amount,
            order_status=order_request.order_status,
        )

    def delete_order(self, order_id: int) -> None:
        if self.order_repository.get_by_id(order_id) is None:
            raise ApplicationError("Замовлення не знайдено.")
        self.order_repository.delete(order_id)

    def _build_order_summary(self, row: tuple) -> OrderSummary:
        client = self.client_repository.get_by_id(int(row[1]))
        build = self.pc_build_repository.get_by_id(int(row[2]))
        return OrderSummary(
            order_id=int(row[0]),
            client_name=client[1] if client else "—",
            build_label=self._build_label(build),
            order_date=str(row[4]),
            production_time=int(row[3]),
            payment_status=str(row[5]),
            due_amount=float(row[6]),
            order_status=str(row[7]),
        )

    def _build_label(self, build: tuple | None) -> str:
        if build is None:
            return "—"
        gpu = self.component_repository.get_by_id("GPU", int(build[1]))
        gpu_name = gpu[3] if gpu else "GPU"
        return f"{build[8]} · {gpu_name}"

    def _ensure_client_exists(self, client_id: int) -> None:
        if self.client_repository.get_by_id(client_id) is None:
            raise ApplicationError("Клієнта не знайдено. Зареєструйте клієнта та повторіть спробу.")

    def _get_total_price(self, build_id: int) -> float:
        total_price = self.pc_build_repository.get_total_price(build_id)
        if total_price is None:
            raise ApplicationError("Збірку ПК з таким ID не знайдено.")
        return total_price

    def _validate_order_request(self, order_request: OrderRequest) -> None:
        if order_request.production_time < 1:
            raise ApplicationError("Час зборки має бути більшим за нуль.")
        if order_request.payment_status not in self.PAYMENT_STATUSES:
            raise ApplicationError("Оберіть коректний статус оплати.")
        if order_request.order_status not in self.ORDER_STATUSES:
            raise ApplicationError("Оберіть коректний статус замовлення.")

    def _calculate_due_amount(self, total_price: float, payment_status: str) -> float:
        return total_price if payment_status == self.UNPAID_STATUS else 0.0

    def _persist_order_transactionally(self, order_request: OrderRequest, order_date: date, due_amount: float) -> None:
        if not hasattr(self.order_repository, "connection") or not hasattr(self.order_repository, "create_without_commit"):
            self.order_repository.create(
                client_id=order_request.client_id,
                pc_build_id=order_request.pc_build_id,
                production_time=order_request.production_time,
                order_date=order_date,
                payment_status=order_request.payment_status,
                due_amount=due_amount,
                order_status=order_request.order_status,
            )
            return

        connection = self.order_repository.connection
        try:
            connection.begin()
            self.order_repository.create_without_commit(
                client_id=order_request.client_id,
                pc_build_id=order_request.pc_build_id,
                production_time=order_request.production_time,
                order_date=order_date,
                payment_status=order_request.payment_status,
                due_amount=due_amount,
                order_status=order_request.order_status,
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    def _get_component_summary(self, build_id: int) -> tuple:
        component_summary = self.pc_build_repository.get_component_summary(build_id)
        if component_summary is None:
            raise ApplicationError("Не вдалося сформувати чек для цієї збірки.")
        return component_summary

    def _build_receipt(self, order_date: date, due_amount: float, component_summary: tuple) -> OrderReceipt:
        return OrderReceipt(
            order_date=order_date,
            due_amount=due_amount,
            total_price=float(component_summary[-1]),
            components=self._build_receipt_components(component_summary),
        )

    def _build_receipt_components(self, component_summary: tuple) -> list[tuple[str, tuple]]:
        components = []
        for table_name, component_id in zip(self.COMPONENT_NAMES, component_summary[:-1]):
            component = self.component_repository.get_by_id(table_name, component_id)
            if component is None:
                raise ApplicationError(f"Не знайдено компонент {table_name} з ID {component_id}.")
            components.append((table_name, component[1:]))
        return components
