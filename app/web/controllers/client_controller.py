from __future__ import annotations

from flask import flash, redirect, request, url_for
from pymysql.err import MySQLError

from app.models import ClientRegistration
from app.web.forms import validate_client_form
from app.web.rendering import page_renderer
from app.web.runtime import services


def register_client_routes(app) -> None:
    @app.route("/clients", methods=["GET", "POST"], endpoint="clients")
    def clients() -> str:
        current_services = services()
        preset_phone = request.args.get("phone", "").strip()
        next_target = request.args.get("next", "").strip()

        if request.method == "POST":
            registration = ClientRegistration(
                full_name=request.form.get("full_name", "").strip(),
                birth_date=request.form.get("birth_date", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
            )
            error_message = validate_client_form(registration)
            if error_message:
                flash(error_message, "error")
            else:
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
                    flash(f"Не вдалося зареєструвати клієнта: {error}", "error")

        return page_renderer(current_services).render_clients(preset_phone=preset_phone)
