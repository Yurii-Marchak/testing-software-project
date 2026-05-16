from app.config import DatabaseConfig
from app.models import BuildSummary, ClientSummary, DashboardStats, OrderSummary
from app.web.app import create_web_app
from app.web.dependencies import ServiceContainer


class FakeConnection:
    def close(self):
        return None


class FakeClientService:
    def register_client(self, registration):
        return 7

    def list_clients(self):
        return [
            ClientSummary(1, "Іван Петренко", "1990-01-01", "+380501234567", "ivan@example.com"),
        ]

    def get_client(self, client_id):
        return ClientSummary(client_id, "Іван Петренко", "1990-01-01", "+380501234567", "ivan@example.com")


class FakeComponentOption:
    def __init__(self, component_id, label):
        self.component_id = component_id
        self.label = label


class FakePcBuildService:
    def __init__(self):
        self.created_builds = []

    def list_builds(self):
        return [
            BuildSummary(1, "Ігрова", "RTX 4070", "Ryzen 7", "B650", "DDR5 32GB", "750W", "NZXT", 55000.0, "#1 | Ігрова | 55000.00 грн"),
        ]

    def list_components(self, table_name):
        component_rows = {
            "GPU": ((1, "RTX 4070", "MSI", "RTX 4070", 12288, "GDDR6X", 3, 215, 750, 55000.0),),
            "CPU": ((1, "Ryzen 7 7700", "AMD", 65, 8, 16, 5, 3.8, 5.3, "DDR5", 14000.0),),
            "Motherboard": ((1, "B650 Tomahawk", "MSI", "AM5", "B650", 4, 6400, "ATX", "DDR5", 9000.0),),
            "RAM": ((1, "DDR5 32GB", "Kingston", 32768, 6000, "DDR5", 2, 6000.0),),
            "PSU": ((1, "750W Gold", "Seasonic", 750, "80+ Gold", "ATX", True, 5000.0),),
            "PC_Case": ((1, "NZXT H6", "NZXT", "ATX", True, 3, 7000.0),),
        }
        return component_rows.get(table_name, ())

    def list_component_options(self, table_name):
        return [FakeComponentOption(1, f"#1 | {table_name}: demo")]

    def create_build(self, build_request):
        self.created_builds.append(build_request)


class FakeReceipt:
    order_date = "2026-05-15"
    due_amount = 0.0
    total_price = 55000.0
    components = [("GPU", ("RTX 4070",))]


class FakeOrderService:
    PAYMENT_STATUSES = ("paid", "unpaid")
    ORDER_STATUSES = ("ready", "not_ready")
    PAYMENT_STATUS_LABELS = {"paid": "Сплачено", "unpaid": "Не сплачено"}
    ORDER_STATUS_LABELS = {"ready": "Готово", "not_ready": "Не готово"}
    UNPAID_STATUS = "unpaid"

    def __init__(self):
        self.last_order_request = None

    def list_orders(self):
        return [
            OrderSummary(1, "Іван Петренко", "Ігрова · RTX 4070", "2026-05-15", 5, "paid", 0.0, "ready"),
        ]

    def build_dashboard_stats(self, clients_count, builds_count):
        return DashboardStats(1, clients_count, builds_count, 0)

    def create_order(self, order_request):
        self.last_order_request = order_request
        return FakeReceipt()


def build_test_app(monkeypatch):
    import app.web.runtime as runtime

    fake_client_service = FakeClientService()
    fake_pc_build_service = FakePcBuildService()
    fake_order_service = FakeOrderService()

    monkeypatch.setattr(runtime, "create_connection", lambda config: FakeConnection())
    monkeypatch.setattr(
        runtime,
        "build_services",
        lambda connection: ServiceContainer(
            client_service=fake_client_service,
            pc_build_service=fake_pc_build_service,
            order_service=fake_order_service,
        ),
    )

    app = create_web_app(DatabaseConfig("localhost", "root", "secret", "lab7"))
    app.config["TESTING"] = True
    return app, fake_pc_build_service, fake_order_service


def test_home_page_returns_200(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200


def test_clients_post_redirects_after_success(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.post(
            "/clients",
            data={
                "full_name": "Іван Петренко",
                "birth_date": "1990-01-01",
                "email": "ivan@example.com",
                "phone": "+380501234567",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/clients")


def test_orders_page_returns_200(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.get("/orders")

    assert response.status_code == 200


def test_builds_post_redirects_after_success(monkeypatch):
    app, fake_pc_build_service, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.post(
            "/builds",
            data={
                "gpu_id": "1",
                "cpu_id": "1",
                "motherboard_id": "1",
                "ram_id": "1",
                "psu_id": "1",
                "pc_case_id": "1",
                "build_type": "Ігрова",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/builds")
    assert len(fake_pc_build_service.created_builds) == 1


def test_orders_post_redirects_and_stores_receipt_in_session(monkeypatch):
    app, _, fake_order_service = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.post(
            "/orders",
            data={
                "client_id": "1",
                "pc_build_id": "1",
                "production_time": "5",
                "payment_status": "paid",
                "order_status": "ready",
            },
        )

        with client.session_transaction() as session_state:
            stored_receipt = session_state.get("last_receipt")
            stored_client = session_state.get("last_selected_client")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/orders")
    assert fake_order_service.last_order_request is not None
    assert fake_order_service.last_order_request.client_id == 1
    assert stored_receipt is not None
    assert stored_receipt["total_price"] == 55000.0
    assert stored_client is not None
    assert stored_client["client_id"] == 1


def test_orders_redirect_page_renders_receipt(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.post(
            "/orders",
            data={
                "client_id": "1",
                "pc_build_id": "1",
                "production_time": "5",
                "payment_status": "paid",
                "order_status": "ready",
            },
            follow_redirects=True,
        )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Чек останньої операції" in page
    assert "RTX 4070" in page


def test_custom_404_page_is_returned(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)

    with app.test_client() as client:
        response = client.get("/missing-page")

    assert response.status_code == 404
    assert "404" in response.get_data(as_text=True)


def test_custom_500_page_is_returned(monkeypatch):
    app, _, _ = build_test_app(monkeypatch)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/boom-for-test")
    def boom_for_test():
        raise RuntimeError("boom")

    with app.test_client() as client:
        response = client.get("/boom-for-test")

    assert response.status_code == 500
    assert "500" in response.get_data(as_text=True)
