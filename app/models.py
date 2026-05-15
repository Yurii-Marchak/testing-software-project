from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ClientRegistration:
    full_name: str
    birth_date: str
    email: str
    phone: str


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
class OrderRequest:
    client_name: str
    client_phone: str
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
