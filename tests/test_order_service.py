from datetime import date

import pytest

from app.exceptions import ApplicationError
from app.models import OrderRequest
from app.services.order_service import OrderService


class FakeClientRepository:
    def __init__(self, clients=None):
        self.clients = clients or {}

    def get_by_id(self, client_id):
        return self.clients.get(client_id)


class FakeComponentRepository:
    def __init__(self, components=None):
        self.components = components or {}

    def get_by_id(self, table_name, component_id):
        return self.components.get((table_name, component_id))


class FakePcBuildRepository:
    def __init__(self, total_price=0.0, build=None, component_summary=None):
        self.total_price = total_price
        self.build = build
        self.component_summary = component_summary

    def get_total_price(self, build_id):
        return self.total_price if build_id == 1 else None

    def get_by_id(self, build_id):
        return self.build if build_id == 1 else None

    def get_component_summary(self, build_id):
        return self.component_summary if build_id == 1 else None


class FakeOrderRepository:
    def __init__(self):
        self.created_orders = []

    def create(self, **kwargs):
        self.created_orders.append(kwargs)

    def list_all(self):
        return ()


def build_service():
    clients = {1: (1, "Іван Петренко", "1990-01-01", "ivan@example.com", "+380501234567")}
    components = {
        ("GPU", 11): (11, "RTX 4070", "MSI", "RTX 4070"),
        ("CPU", 12): (12, "Ryzen 7 7700", "AMD"),
        ("Motherboard", 13): (13, "B650 Tomahawk", "MSI"),
        ("RAM", 14): (14, "Kingston Fury 32GB", "Kingston"),
        ("PSU", 15): (15, "Seasonic 850W", "Seasonic"),
        ("PC_Case", 16): (16, "NZXT H6 Flow", "NZXT"),
    }
    build = (1, 11, 12, 13, 14, 15, 16, 56000.0, "Gaming")
    summary = (11, 12, 13, 14, 15, 16, 56000.0)
    order_repository = FakeOrderRepository()
    service = OrderService(
        FakeClientRepository(clients),
        FakeComponentRepository(components),
        FakePcBuildRepository(total_price=56000.0, build=build, component_summary=summary),
        order_repository,
    )
    return service, order_repository


def test_create_order_sets_due_amount_for_unpaid_request():
    service, order_repository = build_service()
    request = OrderRequest(
        client_id=1,
        pc_build_id=1,
        production_time=5,
        payment_status="Не сплачено",
        order_status="Не готово",
    )

    receipt = service.create_order(request)

    assert receipt.due_amount == 56000.0
    assert receipt.total_price == 56000.0
    assert len(receipt.components) == 6
    assert order_repository.created_orders[0]["due_amount"] == 56000.0
    assert order_repository.created_orders[0]["order_date"] == date.today()


def test_create_order_rejects_invalid_payment_status():
    service, _ = build_service()
    request = OrderRequest(
        client_id=1,
        pc_build_id=1,
        production_time=5,
        payment_status="Невідомо",
        order_status="Не готово",
    )

    with pytest.raises(ApplicationError, match="статус оплати"):
        service.create_order(request)


def test_create_order_rejects_missing_client():
    service, _ = build_service()
    request = OrderRequest(
        client_id=99,
        pc_build_id=1,
        production_time=5,
        payment_status="Сплачено",
        order_status="Готово",
    )

    with pytest.raises(ApplicationError, match="Клієнта не знайдено"):
        service.create_order(request)
