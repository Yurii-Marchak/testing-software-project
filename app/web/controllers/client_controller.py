from __future__ import annotations

from flask import flash, redirect, request, url_for
from pymysql.err import MySQLError

from app.exceptions import ApplicationError
from app.web.forms import build_client_registration, validate_client_form
from app.web.rendering import page_renderer
from app.web.runtime import services


def register_client_routes(app) -> None:
    @app.route("/clients", methods=["GET", "POST"], endpoint="clients")
    def clients() -> str:
        current_services = services()
        preset_phone = request.args.get("phone", "").strip()
        next_target = request.args.get("next", "").strip()
        edit_client_id = request.args.get("edit_client_id", "").strip()

        if request.method == "POST":
            action = request.form.get("action", "create").strip()
            if action == "delete":
                return _delete_client(current_services)
            return _save_client(current_services, preset_phone, next_target, action)

        client_form_values = {}
        open_client_modal = False
        if edit_client_id:
            client = current_services.client_service.get_client_form_values(int(edit_client_id))
            if client is not None:
                client_form_values = client
                open_client_modal = True

        return page_renderer(current_services).render_clients(
            preset_phone=preset_phone,
            client_form_values=client_form_values,
            open_client_modal=open_client_modal,
        )


def _save_client(current_services, preset_phone: str, next_target: str, action: str):
    registration, form_values = build_client_registration(request.form)
    error_message = validate_client_form(registration, form_values)
    if error_message:
        return page_renderer(current_services).render_clients(
            preset_phone=form_values.get("phone", preset_phone),
            client_form_error=error_message,
            client_form_values=form_values,
            open_client_modal=True,
        )

    try:
        if action == "update":
            client_id = int(request.form.get("client_id", "0"))
            current_services.client_service.update_client(client_id, registration)
            flash("Клієнта успішно оновлено.", "success")
        else:
            client_id = current_services.client_service.register_client(registration)
            flash(f"Клієнта успішно зареєстровано. ID: {client_id}", "success")
            if next_target == "orders":
                return redirect(
                    url_for(
                        "orders",
                        phone_query=registration.phone,
                        created_client=client_id,
                        open_order_modal="1",
                    )
                )
        return redirect(url_for("clients"))
    except (ApplicationError, MySQLError) as error:
        return page_renderer(current_services).render_clients(
            preset_phone=form_values.get("phone", preset_phone),
            client_form_error=_format_client_error(error),
            client_form_values=form_values | {"client_id": request.form.get("client_id", "").strip()},
            open_client_modal=True,
        )


def _delete_client(current_services):
    try:
        client_id = int(request.form.get("client_id", "0"))
        current_services.client_service.delete_client(client_id)
        flash("Клієнта видалено.", "success")
    except (ApplicationError, MySQLError) as error:
        flash(_format_client_error(error), "error")
    return redirect(url_for("clients"))


def _format_client_error(error: Exception) -> str:
    if isinstance(error, MySQLError) and getattr(error, "args", None):
        message = str(error.args[-1]).lower()
        if "email" in message and "duplicate" in message:
            return "Клієнт із таким email уже існує."
        if "phone" in message and "duplicate" in message:
            return "Клієнт із таким номером телефону вже існує."
        if "too long" in message:
            return "Одне з полів перевищує допустиму довжину."
        if "foreign key" in message or "constraint" in message:
            return "Неможливо видалити клієнта, який використовується в замовленнях."
    return str(error)
