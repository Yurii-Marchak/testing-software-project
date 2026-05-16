from __future__ import annotations

from flask import flash, redirect, request, url_for
from pymysql.err import MySQLError

from app.web.forms import build_client_registration, validate_client_form
from app.web.rendering import page_renderer
from app.web.runtime import services


def register_client_routes(app) -> None:
    @app.route("/clients", methods=["GET", "POST"], endpoint="clients")
    def clients() -> str:
        current_services = services()
        preset_phone = request.args.get("phone", "").strip()
        next_target = request.args.get("next", "").strip()

        if request.method == "POST":
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
            except MySQLError as error:
                return page_renderer(current_services).render_clients(
                    preset_phone=form_values.get("phone", preset_phone),
                    client_form_error=_format_client_error(error),
                    client_form_values=form_values,
                    open_client_modal=True,
                )

        return page_renderer(current_services).render_clients(preset_phone=preset_phone)


def _format_client_error(error: MySQLError) -> str:
    if getattr(error, "args", None):
        message = str(error.args[-1]).lower()
        if "email" in message and "duplicate" in message:
            return "Клієнт із таким email уже існує."
        if "phone" in message and "duplicate" in message:
            return "Клієнт із таким номером телефону вже існує."
        if "too long" in message:
            return "Одне з полів перевищує допустиму довжину."
    return f"Не вдалося зареєструвати клієнта: {error}"
