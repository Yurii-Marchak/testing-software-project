from __future__ import annotations

from datetime import datetime, timedelta

from flask import flash, redirect, request, session, url_for
from pymysql.err import MySQLError

from app.exceptions import ApplicationError
from app.web.forms import parse_order_form
from app.web.rendering import page_renderer
from app.web.runtime import services
from app.web.serializers import serialize_client, serialize_receipt


def register_order_routes(app) -> None:
    @app.route("/orders", methods=["GET", "POST"], endpoint="orders")
    def orders() -> str:
        current_services = services()
        phone_query = request.args.get("phone_query", "").strip()
        receipt = session.pop("last_receipt", None)
        selected_client = session.pop("last_selected_client", None)
        created_client_id = request.args.get("created_client", "").strip()
        open_order_modal = request.args.get("open_order_modal") == "1"
        edit_order_id = request.args.get("edit_order_id", "").strip()

        if request.method == "POST":
            action = request.form.get("action", "create").strip()
            if action == "delete":
                return _delete_order(current_services)
            return _save_order(
                current_services,
                phone_query=phone_query,
                receipt=receipt,
                selected_client=selected_client,
                created_client_id=created_client_id,
                action=action,
            )

        order_form_values = {}
        if edit_order_id:
            order_form_values = _build_edit_order_values(current_services, int(edit_order_id))
            open_order_modal = bool(order_form_values)

        return page_renderer(current_services).render_orders(
            receipt=receipt,
            phone_query=phone_query,
            selected_client=selected_client,
            created_client_id=created_client_id,
            open_order_modal=open_order_modal,
            order_form_values=order_form_values,
        )


def _save_order(current_services, phone_query: str, receipt, selected_client, created_client_id: str, action: str):
    form_values = {
        "order_id": request.form.get("order_id", "").strip(),
        "client_id": request.form.get("client_id", "").strip(),
        "pc_build_id": request.form.get("pc_build_id", "").strip(),
        "production_deadline": request.form.get("production_deadline", "").strip(),
        "payment_status": request.form.get("payment_status", "").strip(),
        "order_status": request.form.get("order_status", "").strip(),
    }
    order_request = parse_order_form(request.form)
    if isinstance(order_request, str):
        return page_renderer(current_services).render_orders(
            receipt=receipt,
            phone_query=phone_query,
            selected_client=selected_client,
            created_client_id=created_client_id,
            open_order_modal=True,
            order_form_error=order_request,
            order_form_values=form_values,
        )

    try:
        if action == "update":
            order_id = int(request.form.get("order_id", "0"))
            current_services.order_service.update_order(order_id, order_request)
            flash("Замовлення успішно оновлено.", "success")
            return redirect(url_for("orders"))

        created_receipt = current_services.order_service.create_order(order_request)
        created_client = current_services.client_service.get_client(order_request.client_id)
        session["last_receipt"] = serialize_receipt(created_receipt)
        session["last_selected_client"] = serialize_client(created_client)
        flash("Замовлення успішно оформлено.", "success")
        return redirect(url_for("orders"))
    except (ApplicationError, MySQLError) as error:
        return page_renderer(current_services).render_orders(
            receipt=receipt,
            phone_query=phone_query,
            selected_client=selected_client,
            created_client_id=created_client_id,
            open_order_modal=True,
            order_form_error=str(error),
            order_form_values=form_values,
        )


def _delete_order(current_services):
    try:
        order_id = int(request.form.get("order_id", "0"))
        current_services.order_service.delete_order(order_id)
        flash("Замовлення видалено.", "success")
    except (ApplicationError, MySQLError) as error:
        flash(str(error), "error")
    return redirect(url_for("orders"))


def _build_edit_order_values(current_services, order_id: int) -> dict[str, str]:
    order_values = current_services.order_service.get_order_form_values(order_id)
    if not order_values:
        return {}

    try:
        production_days = int(order_values.get("production_time", "1"))
    except ValueError:
        production_days = 1
    deadline = datetime.now() + timedelta(days=max(1, production_days))
    order_values["production_deadline"] = deadline.strftime("%Y-%m-%dT%H:%M")
    return order_values
