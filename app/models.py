from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ClientRegistration:
    full_name: str
    birth_date: str
    email: str
    phone: str


@dataclass(frozen=True)
class ClientSummary:
    client_id: int
    full_name: str
    birth_date: str
    phone: str
    email: str


@dataclass(frozen=True)
class ComponentOption:
    component_id: int
    label: str


@dataclass(frozen=True)
class PcBuildRequest:
    gpu_id: int
    cpu_id: int
    motherboard_id: int
    ram_id: int
    psu_id: int
    pc_case_id: int
    build_type: str


@dataclass(frozen=True)
class BuildSummary:
    build_id: int
    build_type: str
    gpu_name: str
    cpu_name: str
    motherboard_name: str
    ram_name: str
    psu_name: str
    pc_case_name: str
    total_price: float
    label: str


@dataclass(frozen=True)
class OrderRequest:
    client_id: int
    pc_build_id: int
    production_time: int
    payment_status: str
    order_status: str


@dataclass(frozen=True)
class OrderReceipt:
    order_date: date
    due_amount: float
    total_price: float
    components: list[tuple[str, tuple]]


@dataclass(frozen=True)
class OrderSummary:
    order_id: int
    client_name: str
    build_label: str
    order_date: str
    production_time: int
    payment_status: str
    due_amount: float
    order_status: str


@dataclass(frozen=True)
class DashboardStats:
    orders_count: int
    clients_count: int
    builds_count: int
    unpaid_count: int
