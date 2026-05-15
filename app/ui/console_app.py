from pymysql.err import MySQLError

from app.exceptions import ApplicationError
from app.models import ClientRegistration, OrderReceipt, OrderRequest, PcBuildRequest
from app.services.client_service import ClientService
from app.services.order_service import OrderService
from app.services.pc_build_service import PcBuildService


class ConsoleApp:
    def __init__(
        self,
        client_service: ClientService,
        pc_build_service: PcBuildService,
        order_service: OrderService,
    ) -> None:
        self.client_service = client_service
        self.pc_build_service = pc_build_service
        self.order_service = order_service

    def run(self) -> None:
        while True:
            print("\n1. Зареєструвати нового клієнта")
            print("2. Створити нову збірку ПК")
            print("3. Створити нове замовлення")
            print("4. Вийти")
            choice = input("Виберіть дію: ").strip()

            if choice == "1":
                self._register_client()
            elif choice == "2":
                self._create_pc_build()
            elif choice == "3":
                self._create_order()
            elif choice == "4":
                print("Вихід з програми.")
                break
            else:
                print("Невірний вибір. Спробуйте ще раз.")

    def _register_client(self) -> None:
        registration = ClientRegistration(
            full_name=input("Введіть повне ім'я клієнта: ").strip(),
            birth_date=input("Введіть дату народження клієнта (РРРР-ММ-ДД): ").strip(),
            email=input("Введіть email клієнта: ").strip(),
            phone=input("Введіть номер телефону клієнта: ").strip(),
        )
        try:
            self.client_service.register_client(registration)
            print("\nКлієнта успішно зареєстровано.")
        except MySQLError as error:
            print("Помилка реєстрації клієнта:", error)

    def _create_pc_build(self) -> None:
        try:
            build_request = PcBuildRequest(
                gpu_id=self._choose_component("GPU"),
                cpu_id=self._choose_component("CPU"),
                motherboard_id=self._choose_component("Motherboard"),
                ram_id=self._choose_component("RAM"),
                psu_id=self._choose_component("PSU"),
                pc_case_id=self._choose_component("PC_Case"),
                build_type=input(
                    "Введіть тип збірки (наприклад, Бюджетна, Геймерська): "
                ).strip(),
            )
            self.pc_build_service.create_build(build_request)
            print("\nЗбірку ПК успішно створено.")
        except (ApplicationError, MySQLError) as error:
            print("Помилка створення збірки ПК:", error)

    def _create_order(self) -> None:
        try:
            builds = self.order_service.list_builds()
            if not builds:
                print("\nНемає доступних збірок ПК для замовлення.")
                return

            print("\nОберіть ПК для замовлення:")
            for build in builds:
                print(f"{build[0]}: {build[1:]}")

            order_request = OrderRequest(
                client_name=input("Введіть ім'я клієнта: ").strip(),
                client_phone=input("Введіть номер телефону клієнта: ").strip(),
                pc_build_id=self._choose_build_id(builds),
                production_time=int(input("Введіть час зборки ПК (у днях): ")),
                payment_status=input("Статус оплати (Сплачено/Не сплачено): ").strip(),
                order_status=input("Статус замовлення (Готово/Не готово): ").strip(),
            )
            receipt = self.order_service.create_order(order_request)
            print("\nКлієнта знайдено!")
            self._print_receipt(receipt)
        except ValueError:
            print("Будь ласка, введіть коректне числове значення.")
        except (ApplicationError, MySQLError) as error:
            print("Помилка створення замовлення:", error)

    def _choose_component(self, table_name: str) -> int:
        while True:
            rows = self.pc_build_service.list_components(table_name)
            self._print_table(table_name, rows)
            try:
                component_id = int(input(f"\nВиберіть {table_name} за ID: "))
            except ValueError:
                print("Будь ласка, введіть коректний ID.")
                continue

            if any(row[0] == component_id for row in rows):
                return component_id
            print("Неправильний ID. Спробуйте ще раз.")

    def _choose_build_id(self, builds: tuple[tuple, ...]) -> int:
        while True:
            try:
                build_id = int(input("Введіть ID ПК: "))
            except ValueError:
                print("Будь ласка, введіть коректний ID.")
                continue

            if any(build[0] == build_id for build in builds):
                return build_id
            print("Неправильний ID. Спробуйте ще раз.")

    def _print_table(self, table_name: str, rows: tuple[tuple, ...]) -> None:
        print(f"\n{table_name}:")
        for row in rows:
            print(row)

    def _print_receipt(self, receipt: OrderReceipt) -> None:
        print("\nЧек:")
        for component_name, component_data in receipt.components:
            print(f"{component_name}: {component_data}")
        print(f"Загальна ціна: {receipt.total_price}")
        print(f"Сума до сплати: {receipt.due_amount}")
