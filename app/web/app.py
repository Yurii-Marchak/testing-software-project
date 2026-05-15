from __future__ import annotations

from flask import Flask, flash, g, render_template, request, url_for
from pymysql.err import MySQLError

from app.config import DatabaseConfig, load_app_secret_key
from app.exceptions import ApplicationError
from app.infrastructure.database import create_connection
from app.models import ClientRegistration, OrderRequest, PcBuildRequest
from app.web.dependencies import ServiceContainer, build_services


def create_web_app(config: DatabaseConfig) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["DATABASE_CONFIG"] = config
    app.config["SECRET_KEY"] = load_app_secret_key()

    @app.before_request
    def before_request() -> None:
        database_config: DatabaseConfig = app.config["DATABASE_CONFIG"]
        connection = create_connection(database_config)
        if connection is None:
            raise RuntimeError("Не вдалося підключитися до бази даних.")
        g.db_connection = connection
        g.services = build_services(connection)

    @app.teardown_request
    def teardown_request(exception: BaseException | None) -> None:
        connection = getattr(g, "db_connection", None)
        if connection is not None:
            connection.close()

    @app.context_processor
    def inject_navigation():
        return {"current_path": request.path}

    @app.get("/")
    def home():
        services = _services()
        orders = services.order_service.list_orders()
        clients = services.client_service.list_clients()
        builds = services.pc_build_service.list_builds()
        stats = services.order_service.build_dashboard_stats(len(clients), len(builds))
        return render_template(
            "dashboard.html",
            stats=stats,
            recent_orders=orders[:8],
        )

    @app.route("/clients", methods=["GET", "POST"])
    def clients():
        services = _services()
        preset_phone = request.args.get("phone", "").strip()

        if request.method == "POST":
            registration = ClientRegistration(
                full_name=request.form.get("full_name", "").strip(),
                birth_date=request.form.get("birth_date", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
            )
            error_message = _validate_client_form(registration)
            if error_message:
                flash(error_message, "error")
            else:
                try:
                    client_id = services.client_service.register_client(registration)
                    flash(f"Клієнта успішно зареєстровано. ID: {client_id}", "success")
                except MySQLError as error:
                    flash(f"Не вдалося зареєструвати клієнта: {error}", "error")

        client_rows = services.client_service.list_clients()
        return render_template(
            "clients.html",
            clients=client_rows,
            clients_json=[
                {
                    "id": client.client_id,
                    "full_name": client.full_name,
                    "birth_date": client.birth_date,
                    "email": client.email,
                    "phone": client.phone,
                }
                for client in client_rows
            ],
            preset_phone=preset_phone,
        )

    @app.route("/builds", methods=["GET", "POST"])
    def builds():
        services = _services()
        component_options = _component_options(services)

        if request.method == "POST":
            build_request = _parse_build_form(request.form)
            if isinstance(build_request, str):
                flash(build_request, "error")
            else:
                try:
                    services.pc_build_service.create_build(build_request)
                    flash("Збірку ПК успішно створено.", "success")
                except (ApplicationError, MySQLError) as error:
                    flash(str(error), "error")

        build_rows = services.pc_build_service.list_builds()
        return render_template(
            "builds.html",
            component_options=component_options,
            builds=build_rows,
            build_catalog_json=_build_catalog_json(services),
        )

    @app.route("/orders", methods=["GET", "POST"])
    def orders():
        services = _services()
        phone_query = request.values.get("phone_query", "").strip()
        clients_list = services.client_service.list_clients(phone_query)
        builds_list = services.pc_build_service.list_builds()
        orders_list = services.order_service.list_orders()
        receipt = None
        selected_client = None
        show_register_prompt = bool(phone_query and not clients_list)

        if request.method == "POST":
            action = request.form.get("action")
            if action == "search":
                if show_register_prompt:
                    flash(
                        "Клієнта з таким номером не знайдено. Ви можете зареєструвати його нижче.",
                        "error",
                    )
            else:
                order_request = _parse_order_form(request.form)
                if isinstance(order_request, str):
                    flash(order_request, "error")
                else:
                    try:
                        receipt = services.order_service.create_order(order_request)
                        selected_client = services.client_service.get_client(order_request.client_id)
                        orders_list = services.order_service.list_orders()
                        flash("Замовлення успішно оформлено.", "success")
                    except (ApplicationError, MySQLError) as error:
                        flash(str(error), "error")

        return render_template(
            "orders.html",
            clients=clients_list,
            builds=builds_list,
            orders=orders_list,
            payment_statuses=services.order_service.PAYMENT_STATUSES,
            order_statuses=services.order_service.ORDER_STATUSES,
            receipt=receipt,
            phone_query=phone_query,
            show_register_prompt=show_register_prompt,
            selected_client=selected_client,
            register_url=url_for("clients", phone=phone_query),
            clients_json=[
                {
                    "id": client.client_id,
                    "full_name": client.full_name,
                    "birth_date": client.birth_date,
                    "email": client.email,
                    "phone": client.phone,
                }
                for client in services.client_service.list_clients()
            ],
            builds_json=[
                {
                    "id": build.build_id,
                    "label": build.label,
                    "build_type": build.build_type,
                    "gpu_name": build.gpu_name,
                    "cpu_name": build.cpu_name,
                    "price": build.total_price,
                }
                for build in builds_list
            ],
        )

    @app.get("/components")
    def components():
        services = _services()
        return render_template(
            "components.html",
            gpu_rows=services.pc_build_service.list_components("GPU"),
            cpu_rows=services.pc_build_service.list_components("CPU"),
            motherboard_rows=services.pc_build_service.list_components("Motherboard"),
            ram_rows=services.pc_build_service.list_components("RAM"),
            psu_rows=services.pc_build_service.list_components("PSU"),
            case_rows=services.pc_build_service.list_components("PC_Case"),
        )

    return app


def _services() -> ServiceContainer:
    return g.services


def _component_options(services: ServiceContainer) -> dict[str, list]:
    return {
        "GPU": services.pc_build_service.list_component_options("GPU"),
        "CPU": services.pc_build_service.list_component_options("CPU"),
        "Motherboard": services.pc_build_service.list_component_options("Motherboard"),
        "RAM": services.pc_build_service.list_component_options("RAM"),
        "PSU": services.pc_build_service.list_component_options("PSU"),
        "PC_Case": services.pc_build_service.list_component_options("PC_Case"),
    }


def _build_catalog_json(services: ServiceContainer) -> dict[str, list[dict]]:
    def map_gpu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "gpu_name": str(row[3]),
            "video_memory": int(row[4]),
            "memory_type": str(row[5]),
            "fan_count": int(row[6]),
            "power_consumption": int(row[7]),
            "recommended_psu_power": int(row[8]),
            "price": float(row[9]),
        }

    def map_cpu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "tdp": int(row[3]),
            "cores": int(row[4]),
            "threads": int(row[5]),
            "process_nm": int(row[6]),
            "base_clock": float(row[7]),
            "turbo_clock": float(row[8]),
            "compatible_ram_type": str(row[9]),
            "price": float(row[10]),
        }

    def map_motherboard(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "socket": str(row[3]),
            "chipset": str(row[4]),
            "ram_slots": int(row[5]),
            "max_ram_frequency": int(row[6]),
            "form_factor": str(row[7]),
            "ram_type": str(row[8]),
            "price": float(row[9]),
        }

    def map_ram(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "capacity": int(row[3]),
            "frequency": int(row[4]),
            "ram_type": str(row[5]),
            "kit_count": int(row[6]),
            "price": float(row[7]),
        }

    def map_psu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "power": int(row[3]),
            "certificate": str(row[4]),
            "form_factor": str(row[5]),
            "modularity": bool(row[6]),
            "price": float(row[7]),
        }

    def map_case(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "form_factor": str(row[3]),
            "glass_side_panel": bool(row[4]),
            "included_fans": int(row[5]),
            "price": float(row[6]),
        }

    return {
        "gpu": [map_gpu(row) for row in services.pc_build_service.list_components("GPU")],
        "cpu": [map_cpu(row) for row in services.pc_build_service.list_components("CPU")],
        "motherboard": [map_motherboard(row) for row in services.pc_build_service.list_components("Motherboard")],
        "ram": [map_ram(row) for row in services.pc_build_service.list_components("RAM")],
        "psu": [map_psu(row) for row in services.pc_build_service.list_components("PSU")],
        "pc_case": [map_case(row) for row in services.pc_build_service.list_components("PC_Case")],
    }


def _parse_build_form(form) -> PcBuildRequest | str:
    try:
        return PcBuildRequest(
            gpu_id=int(form.get("gpu_id", "")),
            cpu_id=int(form.get("cpu_id", "")),
            motherboard_id=int(form.get("motherboard_id", "")),
            ram_id=int(form.get("ram_id", "")),
            psu_id=int(form.get("psu_id", "")),
            pc_case_id=int(form.get("pc_case_id", "")),
            build_type=form.get("build_type", "").strip(),
        )
    except ValueError:
        return "Оберіть комплектуючі зі списків."


def _parse_order_form(form) -> OrderRequest | str:
    try:
        production_time = int(form.get("production_time", ""))
    except ValueError:
        return "Час зборки має бути числом."

    try:
        return OrderRequest(
            client_id=int(form.get("client_id", "")),
            pc_build_id=int(form.get("pc_build_id", "")),
            production_time=production_time,
            payment_status=form.get("payment_status", "").strip(),
            order_status=form.get("order_status", "").strip(),
        )
    except ValueError:
        return "Оберіть клієнта та збірку зі списків."


def _validate_client_form(registration: ClientRegistration) -> str | None:
    if not registration.full_name:
        return "Вкажіть ПІБ клієнта."
    if not registration.birth_date:
        return "Вкажіть дату народження."
    if not registration.email:
        return "Вкажіть email клієнта."
    if not registration.phone:
        return "Вкажіть номер телефону клієнта."
    return None
