from __future__ import annotations

from flask import flash, redirect, request, url_for
from pymysql.err import MySQLError

from app.exceptions import ApplicationError
from app.web.forms import parse_build_form
from app.web.rendering import page_renderer
from app.web.runtime import services


def register_build_routes(app) -> None:
    @app.route("/builds", methods=["GET", "POST"], endpoint="builds")
    def builds() -> str:
        current_services = services()
        edit_build_id = request.args.get("edit_build_id", "").strip()

        if request.method == "POST":
            action = request.form.get("action", "create").strip()
            if action == "delete":
                return _delete_build(current_services)
            return _save_build(current_services, action)

        build_form_values = {}
        open_build_modal = False
        if edit_build_id:
            build = current_services.pc_build_service.get_build_form_values(int(edit_build_id))
            if build is not None:
                build_form_values = build
                open_build_modal = True

        return page_renderer(current_services).render_builds_with_state(
            build_form_values=build_form_values,
            open_build_modal=open_build_modal,
        )


def _save_build(current_services, action: str):
    form_values = {
        "build_id": request.form.get("build_id", "").strip(),
        "gpu_id": request.form.get("gpu_id", "").strip(),
        "cpu_id": request.form.get("cpu_id", "").strip(),
        "motherboard_id": request.form.get("motherboard_id", "").strip(),
        "ram_id": request.form.get("ram_id", "").strip(),
        "psu_id": request.form.get("psu_id", "").strip(),
        "pc_case_id": request.form.get("pc_case_id", "").strip(),
        "build_type": request.form.get("build_type", "").strip(),
    }
    build_request = parse_build_form(request.form)
    if isinstance(build_request, str):
        return page_renderer(current_services).render_builds_with_state(
            build_form_error=build_request,
            build_form_values=form_values,
            open_build_modal=True,
        )

    try:
        if action == "update":
            build_id = int(request.form.get("build_id", "0"))
            current_services.pc_build_service.update_build(build_id, build_request)
            flash("Збірку ПК успішно оновлено.", "success")
        else:
            current_services.pc_build_service.create_build(build_request)
            flash("Збірку ПК успішно створено.", "success")
        return redirect(url_for("builds"))
    except (ApplicationError, MySQLError) as error:
        return page_renderer(current_services).render_builds_with_state(
            build_form_error=str(error),
            build_form_values=form_values,
            open_build_modal=True,
        )


def _delete_build(current_services):
    try:
        build_id = int(request.form.get("build_id", "0"))
        current_services.pc_build_service.delete_build(build_id)
        flash("Збірку ПК видалено.", "success")
    except (ApplicationError, MySQLError) as error:
        flash(str(error), "error")
    return redirect(url_for("builds"))
