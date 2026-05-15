from __future__ import annotations

from collections.abc import Mapping

from app.models import ClientRegistration, OrderRequest, PcBuildRequest


def parse_build_form(form: Mapping[str, str]) -> PcBuildRequest | str:
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


def parse_order_form(form: Mapping[str, str]) -> OrderRequest | str:
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


def validate_client_form(registration: ClientRegistration) -> str | None:
    if not registration.full_name:
        return "Вкажіть ПІБ клієнта."
    if not registration.birth_date:
        return "Вкажіть дату народження."
    if not registration.email:
        return "Вкажіть email клієнта."
    if not registration.phone:
        return "Вкажіть номер телефону клієнта."
    return None
