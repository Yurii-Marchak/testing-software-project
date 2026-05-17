from __future__ import annotations

from app.exceptions import ApplicationError
from app.repositories.component_repository import ComponentRepository
from app.services.component_catalog import COMPONENT_CONFIG, ComponentConfig, ComponentField


class ComponentService:
    def __init__(self, component_repository: ComponentRepository) -> None:
        self.component_repository = component_repository

    def list_sections(self) -> list[dict]:
        sections = []
        for table_name, config in COMPONENT_CONFIG.items():
            rows = self.component_repository.list_all(table_name)
            sections.append(
                {
                    "table_name": table_name,
                    "slug": config.slug,
                    "short_label": config.short_label,
                    "title": config.title,
                    "description": config.description,
                    "headers": list(config.headers),
                    "rows": rows,
                }
            )
        return sections

    def get_config(self, table_name: str) -> dict:
        config = self._require_config(table_name)
        return {
            "slug": config.slug,
            "short_label": config.short_label,
            "title": config.title,
            "description": config.description,
            "headers": list(config.headers),
            "fields": [(field.name, field.label, field.field_type) for field in config.fields],
        }

    def get_component_form_data(self, table_name: str, component_id: int) -> dict[str, str] | None:
        config = self._require_config(table_name)
        row = self.component_repository.get_by_id(table_name, component_id)
        if row is None:
            return None
        values = {"component_id": str(row[0]), "table_name": table_name}
        for index, field in enumerate(config.fields, start=1):
            values[field.name] = self._format_value(row[index], field.field_type)
        return values

    def create_component(self, table_name: str, values: dict[str, str]) -> None:
        payload = self._coerce_values(table_name, values)
        self.component_repository.create(table_name, payload)

    def update_component(self, table_name: str, component_id: int, values: dict[str, str]) -> None:
        payload = self._coerce_values(table_name, values)
        self.component_repository.update(table_name, component_id, payload)

    def delete_component(self, table_name: str, component_id: int) -> None:
        self.component_repository.delete(table_name, component_id)

    def _coerce_values(self, table_name: str, values: dict[str, str]) -> dict[str, object]:
        config = self._require_config(table_name)
        payload: dict[str, object] = {}
        for field in config.fields:
            raw_value = values.get(field.name, "").strip()
            if raw_value == "":
                raise ApplicationError(f'Вкажіть поле "{field.label}".')
            try:
                payload[field.name] = self._convert_value(raw_value, field)
            except ValueError as error:
                raise ApplicationError(str(error)) from error
        return payload

    def _convert_value(self, raw_value: str, field: ComponentField) -> object:
        if field.field_type == "integer":
            return int(raw_value)
        if field.field_type == "decimal":
            return float(raw_value)
        if field.field_type == "boolean":
            if raw_value.lower() in {"true", "1", "yes"}:
                return True
            if raw_value.lower() in {"false", "0", "no"}:
                return False
            raise ValueError("Оберіть коректне булеве значення.")
        return raw_value

    def _format_value(self, value: object, field_type: str) -> str:
        if field_type == "boolean":
            return "true" if bool(value) else "false"
        return str(value)

    def _require_config(self, table_name: str) -> ComponentConfig:
        config = COMPONENT_CONFIG.get(table_name)
        if not config:
            raise ApplicationError("Оберіть коректний тип комплектуючого.")
        return config

