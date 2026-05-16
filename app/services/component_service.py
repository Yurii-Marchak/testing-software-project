from __future__ import annotations

from app.exceptions import ApplicationError
from app.repositories.component_repository import ComponentRepository


class ComponentService:
    COMPONENT_CONFIG = {
        "GPU": {
            "slug": "gpu",
            "short_label": "GPU",
            "title": "Відеокарти",
            "description": "Оберіть продуктивну графіку для ігрових і робочих збірок.",
            "headers": ["Модель", "Виробник", "Чіп", "Пам'ять", "Тип", "Вентилятори", "TDP", "Рек. PSU", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("gpu_name", "Чіп", "text"),
                ("video_memory", "Пам'ять (МБ)", "number"),
                ("memory_type", "Тип пам'яті", "text"),
                ("fan_count", "Вентилятори", "number"),
                ("power_consumption", "TDP", "number"),
                ("recommended_psu_power", "Рекомендована потужність PSU", "number"),
                ("price", "Ціна", "number"),
            ],
        },
        "CPU": {
            "slug": "cpu",
            "short_label": "CPU",
            "title": "Процесори",
            "description": "Порівнюйте ядра, потоки та сумісність із пам'яттю.",
            "headers": ["Модель", "Виробник", "TDP", "Ядра", "Потоки", "Техпроцес", "Base", "Turbo", "RAM", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("tdp", "TDP", "number"),
                ("cores", "Ядра", "number"),
                ("threads", "Потоки", "number"),
                ("process_nm", "Техпроцес", "number"),
                ("base_clock", "Base Clock", "number"),
                ("turbo_clock", "Turbo Clock", "number"),
                ("compatible_ram_type", "Підтримка RAM", "text"),
                ("price", "Ціна", "number"),
            ],
        },
        "Motherboard": {
            "slug": "motherboard",
            "short_label": "MB",
            "title": "Материнські плати",
            "description": "Контролюйте сокет, чипсет і форм-фактор без ручного зіставлення.",
            "headers": ["Модель", "Виробник", "Сокет", "Чипсет", "RAM слоти", "Макс. частота", "Форм-фактор", "RAM", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("socket", "Сокет", "text"),
                ("chipset", "Чипсет", "text"),
                ("ram_slots", "RAM слоти", "number"),
                ("max_ram_frequency", "Макс. частота", "number"),
                ("form_factor", "Форм-фактор", "text"),
                ("ram_type", "Тип RAM", "text"),
                ("price", "Ціна", "number"),
            ],
        },
        "RAM": {
            "slug": "ram",
            "short_label": "RAM",
            "title": "Оперативна пам'ять",
            "description": "Зручно оцінюйте тип, обсяг і частоту для майбутньої збірки.",
            "headers": ["Модель", "Виробник", "Обсяг", "Частота", "Тип", "Комплект", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("capacity", "Обсяг (МБ)", "number"),
                ("frequency", "Частота", "number"),
                ("ram_type", "Тип RAM", "text"),
                ("kit_count", "Комплект", "number"),
                ("price", "Ціна", "number"),
            ],
        },
        "PSU": {
            "slug": "psu",
            "short_label": "PSU",
            "title": "Блоки живлення",
            "description": "Перевіряйте потужність і сертифікацію ще до створення збірки.",
            "headers": ["Модель", "Виробник", "Потужність", "Сертифікат", "Форм-фактор", "Модульність", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("power", "Потужність", "number"),
                ("certificate", "Сертифікат", "text"),
                ("form_factor", "Форм-фактор", "text"),
                ("modularity", "Модульність", "boolean"),
                ("price", "Ціна", "number"),
            ],
        },
        "PC_Case": {
            "slug": "cases",
            "short_label": "CASE",
            "title": "Корпуси",
            "description": "Форма, охолодження й сумісність корпусу з усією конфігурацією.",
            "headers": ["Модель", "Виробник", "Форм-фактор", "Скло", "Вентилятори", "Ціна"],
            "fields": [
                ("model_name", "Модель", "text"),
                ("manufacturer", "Виробник", "text"),
                ("form_factor", "Форм-фактор", "text"),
                ("glass_side_panel", "Скло", "boolean"),
                ("included_fans", "Вентилятори", "number"),
                ("price", "Ціна", "number"),
            ],
        },
    }

    def __init__(self, component_repository: ComponentRepository) -> None:
        self.component_repository = component_repository

    def list_sections(self) -> list[dict]:
        sections = []
        for table_name, config in self.COMPONENT_CONFIG.items():
            rows = self.component_repository.list_all(table_name)
            sections.append(
                {
                    "table_name": table_name,
                    "slug": config["slug"],
                    "short_label": config["short_label"],
                    "title": config["title"],
                    "description": config["description"],
                    "headers": config["headers"],
                    "rows": rows,
                }
            )
        return sections

    def get_config(self, table_name: str) -> dict:
        config = self.COMPONENT_CONFIG.get(table_name)
        if not config:
            raise ApplicationError("Оберіть коректний тип комплектуючого.")
        return config

    def get_component_form_data(self, table_name: str, component_id: int) -> dict[str, str] | None:
        config = self.get_config(table_name)
        row = self.component_repository.get_by_id(table_name, component_id)
        if row is None:
            return None
        values = {"component_id": str(row[0]), "table_name": table_name}
        for index, (field_name, _, field_type) in enumerate(config["fields"], start=1):
            values[field_name] = self._format_value(row[index], field_type)
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
        config = self.get_config(table_name)
        payload: dict[str, object] = {}
        for field_name, label, field_type in config["fields"]:
            raw_value = values.get(field_name, "").strip()
            if raw_value == "":
                raise ApplicationError(f"Вкажіть поле «{label}».")
            try:
                payload[field_name] = self._convert_value(raw_value, field_type)
            except ValueError as error:
                raise ApplicationError(str(error)) from error
        return payload

    def _convert_value(self, raw_value: str, field_type: str) -> object:
        if field_type == "number":
            if "." in raw_value:
                return float(raw_value)
            return int(raw_value)
        if field_type == "boolean":
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
