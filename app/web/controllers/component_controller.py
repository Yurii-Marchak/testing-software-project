from __future__ import annotations

from flask import flash, redirect, request, url_for
from pymysql.err import MySQLError

from app.exceptions import ApplicationError
from app.web.rendering import page_renderer
from app.web.runtime import services


def register_component_routes(app) -> None:
    @app.route("/components", methods=["GET", "POST"], endpoint="components")
    def components() -> str:
        current_services = services()
        selected_component_table = request.args.get("table", "").strip()
        edit_component_id = request.args.get("edit_component_id", "").strip()

        if request.method == "POST":
            action = request.form.get("action", "create").strip()
            if action == "delete":
                return _delete_component(current_services)
            return _save_component(current_services, action)

        component_form_values = {"table_name": selected_component_table} if selected_component_table else {}
        open_component_modal = bool(selected_component_table)
        if selected_component_table and edit_component_id:
            form_values = current_services.component_service.get_component_form_data(
                selected_component_table,
                int(edit_component_id),
            )
            if form_values is not None:
                component_form_values = form_values
                open_component_modal = True

        return page_renderer(current_services).render_components_with_state(
            component_form_values=component_form_values,
            selected_component_table=selected_component_table,
            open_component_modal=open_component_modal,
        )


def _save_component(current_services, action: str):
    table_name = request.form.get("table_name", "").strip()
    form_values = {"table_name": table_name, "component_id": request.form.get("component_id", "").strip()}

    try:
        config = current_services.component_service.get_config(table_name)
        for field_name, _, _ in config["fields"]:
            form_values[field_name] = request.form.get(field_name, "").strip()

        if action == "update":
            current_services.component_service.update_component(
                table_name,
                int(form_values["component_id"] or "0"),
                form_values,
            )
            flash("Комплектуючу успішно оновлено.", "success")
        else:
            current_services.component_service.create_component(table_name, form_values)
            flash("Комплектуючу успішно додано.", "success")
        return redirect(url_for("components", table=table_name))
    except (ApplicationError, MySQLError, ValueError) as error:
        return page_renderer(current_services).render_components_with_state(
            component_form_error=str(error),
            component_form_values=form_values,
            selected_component_table=table_name,
            open_component_modal=True,
        )


def _delete_component(current_services):
    table_name = request.form.get("table_name", "").strip()
    try:
        component_id = int(request.form.get("component_id", "0"))
        current_services.component_service.delete_component(table_name, component_id)
        flash("Комплектуючу видалено.", "success")
    except (ApplicationError, MySQLError, ValueError) as error:
        flash(str(error), "error")
    return redirect(url_for("components", table=table_name))
