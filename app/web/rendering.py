from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from flask import render_template

from app.web.dependencies import ServiceContainer
from app.web.serializers import build_catalog_json, build_component_options, serialize_clients


class PageRenderer:
    def __init__(self, services: ServiceContainer) -> None:
        self.services = services

    def render_dashboard(self) -> str:
        orders = self.services.order_service.list_orders()
        clients = self.services.client_service.list_clients()
        builds = self.services.pc_build_service.list_builds()
        stats = self.services.order_service.build_dashboard_stats(len(clients), len(builds))
        return self._render(
            "dashboard.html",
            stats=stats,
            recent_orders=orders[:8],
            unpaid_status=self.services.order_service.UNPAID_STATUS,
            payment_status_labels=self.services.order_service.PAYMENT_STATUS_LABELS,
            order_status_labels=self.services.order_service.ORDER_STATUS_LABELS,
        )

    def render_clients(
        self,
        preset_phone: str = "",
        client_form_error: str = "",
        client_form_values: dict[str, str] | None = None,
        open_client_modal: bool = False,
    ) -> str:
        client_rows = self.services.client_service.list_clients()
        return self._render(
            "clients.html",
            clients=client_rows,
            clients_json=serialize_clients(client_rows),
            preset_phone=preset_phone,
            client_form_error=client_form_error,
            client_form_values=client_form_values or {},
            open_client_modal=open_client_modal,
        )

    def render_builds(self) -> str:
        return self._render(
            "builds.html",
            component_options=build_component_options(self.services),
            builds=self.services.pc_build_service.list_builds(),
            build_catalog_json=build_catalog_json(self.services),
        )

    def render_orders(
        self,
        receipt: dict | None = None,
        phone_query: str = "",
        selected_client: dict | None = None,
        created_client_id: str = "",
        open_order_modal: bool = False,
        order_form_error: str = "",
        order_form_values: dict[str, str] | None = None,
    ) -> str:
        now = datetime.now()
        all_clients = self.services.client_service.list_clients()
        builds_list = self.services.pc_build_service.list_builds()
        orders_list = self.services.order_service.list_orders()
        return self._render(
            "orders.html",
            clients=all_clients,
            all_clients=all_clients,
            builds=builds_list,
            orders=orders_list,
            payment_statuses=self.services.order_service.PAYMENT_STATUSES,
            order_statuses=self.services.order_service.ORDER_STATUSES,
            payment_status_labels=self.services.order_service.PAYMENT_STATUS_LABELS,
            order_status_labels=self.services.order_service.ORDER_STATUS_LABELS,
            unpaid_status=self.services.order_service.UNPAID_STATUS,
            receipt=receipt,
            phone_query=phone_query,
            selected_client=selected_client,
            created_client_id=created_client_id,
            open_order_modal=open_order_modal,
            order_form_error=order_form_error,
            order_form_values=order_form_values or {},
            min_production_deadline=now.strftime("%Y-%m-%dT%H:%M"),
            max_production_deadline=(now + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M"),
            clients_json=serialize_clients(all_clients),
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

    def render_components(self) -> str:
        return self._render(
            "components.html",
            gpu_rows=self.services.pc_build_service.list_components("GPU"),
            cpu_rows=self.services.pc_build_service.list_components("CPU"),
            motherboard_rows=self.services.pc_build_service.list_components("Motherboard"),
            ram_rows=self.services.pc_build_service.list_components("RAM"),
            psu_rows=self.services.pc_build_service.list_components("PSU"),
            case_rows=self.services.pc_build_service.list_components("PC_Case"),
        )

    def _render(self, template_name: str, **context: Any) -> str:
        return render_template(template_name, **context)


def page_renderer(services: ServiceContainer) -> PageRenderer:
    return PageRenderer(services)


def render_error_page(
    title: str,
    code: str,
    heading: str,
    message: str,
    accent: str,
    eyebrow: str,
    details: tuple[str, str],
) -> str:
    return render_template(
        "error.html",
        title=title,
        error_code=code,
        error_heading=heading,
        error_message=message,
        error_accent=accent,
        error_eyebrow=eyebrow,
        error_details=details,
    )
