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

        if request.method == "POST":
            build_request = parse_build_form(request.form)
            if isinstance(build_request, str):
                flash(build_request, "error")
            else:
                try:
                    current_services.pc_build_service.create_build(build_request)
                    flash("Збірку ПК успішно створено.", "success")
                    return redirect(url_for("builds"))
                except (ApplicationError, MySQLError) as error:
                    flash(str(error), "error")

        return page_renderer(current_services).render_builds()
