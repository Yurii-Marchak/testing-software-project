from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComponentField:
    name: str
    label: str
    field_type: str


@dataclass(frozen=True)
class ComponentConfig:
    slug: str
    short_label: str
    title: str
    description: str
    headers: tuple[str, ...]
    fields: tuple[ComponentField, ...]


COMPONENT_CONFIG: dict[str, ComponentConfig] = {
    "GPU": ComponentConfig(
        slug="gpu",
        short_label="GPU",
        title="Відеокарти",
        description="Оберіть продуктивну графіку для ігрових і робочих збірок.",
        headers=("Модель", "Виробник", "Чіп", "Пам'ять", "Тип", "Вентилятори", "TDP", "Рек. PSU", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("gpu_name", "Чіп", "text"),
            ComponentField("video_memory", "Пам'ять (МБ)", "integer"),
            ComponentField("memory_type", "Тип пам'яті", "text"),
            ComponentField("fan_count", "Вентилятори", "integer"),
            ComponentField("power_consumption", "TDP", "integer"),
            ComponentField("recommended_psu_power", "Рекомендована потужність PSU", "integer"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
    "CPU": ComponentConfig(
        slug="cpu",
        short_label="CPU",
        title="Процесори",
        description="Порівнюйте ядра, потоки та сумісність із пам'яттю.",
        headers=("Модель", "Виробник", "TDP", "Ядра", "Потоки", "Техпроцес", "Base", "Turbo", "RAM", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("tdp", "TDP", "integer"),
            ComponentField("cores", "Ядра", "integer"),
            ComponentField("threads", "Потоки", "integer"),
            ComponentField("process_nm", "Техпроцес", "integer"),
            ComponentField("base_clock", "Base Clock", "decimal"),
            ComponentField("turbo_clock", "Turbo Clock", "decimal"),
            ComponentField("compatible_ram_type", "Підтримка RAM", "text"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
    "Motherboard": ComponentConfig(
        slug="motherboard",
        short_label="MB",
        title="Материнські плати",
        description="Контролюйте сокет, чипсет і форм-фактор без ручного зіставлення.",
        headers=("Модель", "Виробник", "Сокет", "Чипсет", "RAM слоти", "Макс. частота", "Форм-фактор", "RAM", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("socket", "Сокет", "text"),
            ComponentField("chipset", "Чипсет", "text"),
            ComponentField("ram_slots", "RAM слоти", "integer"),
            ComponentField("max_ram_frequency", "Макс. частота", "integer"),
            ComponentField("form_factor", "Форм-фактор", "text"),
            ComponentField("ram_type", "Тип RAM", "text"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
    "RAM": ComponentConfig(
        slug="ram",
        short_label="RAM",
        title="Оперативна пам'ять",
        description="Зручно оцінюйте тип, обсяг і частоту для майбутньої збірки.",
        headers=("Модель", "Виробник", "Обсяг", "Частота", "Тип", "Комплект", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("capacity", "Обсяг (МБ)", "integer"),
            ComponentField("frequency", "Частота", "integer"),
            ComponentField("ram_type", "Тип RAM", "text"),
            ComponentField("kit_count", "Комплект", "integer"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
    "PSU": ComponentConfig(
        slug="psu",
        short_label="PSU",
        title="Блоки живлення",
        description="Перевіряйте потужність і сертифікацію ще до створення збірки.",
        headers=("Модель", "Виробник", "Потужність", "Сертифікат", "Форм-фактор", "Модульність", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("power", "Потужність", "integer"),
            ComponentField("certificate", "Сертифікат", "text"),
            ComponentField("form_factor", "Форм-фактор", "text"),
            ComponentField("modularity", "Модульність", "boolean"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
    "PC_Case": ComponentConfig(
        slug="cases",
        short_label="CASE",
        title="Корпуси",
        description="Форма, охолодження й сумісність корпусу з усією конфігурацією.",
        headers=("Модель", "Виробник", "Форм-фактор", "Скло", "Вентилятори", "Ціна"),
        fields=(
            ComponentField("model_name", "Модель", "text"),
            ComponentField("manufacturer", "Виробник", "text"),
            ComponentField("form_factor", "Форм-фактор", "text"),
            ComponentField("glass_side_panel", "Скло", "boolean"),
            ComponentField("included_fans", "Вентилятори", "integer"),
            ComponentField("price", "Ціна", "decimal"),
        ),
    ),
}

