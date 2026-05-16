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


def build_client_registration(form: Mapping[str, str]) -> tuple[ClientRegistration, dict[str, str]]:
    last_name = form.get("last_name", "").strip()
    first_name = form.get("first_name", "").strip()
    birth_date = form.get("birth_date", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()

    full_name = " ".join(part for part in (last_name, first_name) if part).strip()
    registration = ClientRegistration(
        full_name=full_name,
        birth_date=birth_date,
        email=email,
        phone=phone,
    )
    form_values = {
        "last_name": last_name,
        "first_name": first_name,
        "birth_date": birth_date,
        "email": email,
        "phone": phone,
    }
    return registration, form_values


def validate_client_form(registration: ClientRegistration, form_values: Mapping[str, str] | None = None) -> str | None:
    values = form_values or {}
    last_name = values.get("last_name", "").strip()
    first_name = values.get("first_name", "").strip()

    if not last_name:
        return "Вкажіть прізвище клієнта."
    if not first_name:
        return "Вкажіть ім'я клієнта."
    if not registration.birth_date:
        return "Вкажіть дату народження."
    if not registration.email:
        return "Вкажіть email клієнта."
    if not registration.phone:
        return "Вкажіть номер телефону клієнта."
    if len(registration.full_name) > 255:
        return "Ім'я та прізвище разом не повинні перевищувати 255 символів."
    if len(registration.email) > 255:
        return "Email не повинен перевищувати 255 символів."
    if len(registration.phone) > 15:
        return "Номер телефону не повинен перевищувати 15 символів."
    return None
