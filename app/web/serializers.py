from __future__ import annotations

from app.models import ClientSummary, OrderReceipt
from app.web.dependencies import ServiceContainer


def serialize_client(client: ClientSummary | None) -> dict | None:
    if client is None:
        return None
    return {
        "client_id": client.client_id,
        "full_name": client.full_name,
        "birth_date": client.birth_date,
        "email": client.email,
        "phone": client.phone,
    }


def serialize_clients(clients: list[ClientSummary]) -> list[dict]:
    return [
        {
            "id": client.client_id,
            "full_name": client.full_name,
            "birth_date": client.birth_date,
            "email": client.email,
            "phone": client.phone,
        }
        for client in clients
    ]


def serialize_receipt(receipt: OrderReceipt) -> dict:
    return {
        "order_date": str(receipt.order_date),
        "due_amount": receipt.due_amount,
        "total_price": receipt.total_price,
        "components": [
            {"name": component_name, "values": list(component_values)}
            for component_name, component_values in receipt.components
        ],
    }


def build_component_options(services: ServiceContainer) -> dict[str, list]:
    return {
        "GPU": services.pc_build_service.list_component_options("GPU"),
        "CPU": services.pc_build_service.list_component_options("CPU"),
        "Motherboard": services.pc_build_service.list_component_options("Motherboard"),
        "RAM": services.pc_build_service.list_component_options("RAM"),
        "PSU": services.pc_build_service.list_component_options("PSU"),
        "PC_Case": services.pc_build_service.list_component_options("PC_Case"),
    }


def build_catalog_json(services: ServiceContainer) -> dict[str, list[dict]]:
    def map_gpu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "gpu_name": str(row[3]),
            "video_memory": int(row[4]),
            "memory_type": str(row[5]),
            "fan_count": int(row[6]),
            "power_consumption": int(row[7]),
            "recommended_psu_power": int(row[8]),
            "price": float(row[9]),
        }

    def map_cpu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "tdp": int(row[3]),
            "cores": int(row[4]),
            "threads": int(row[5]),
            "process_nm": int(row[6]),
            "base_clock": float(row[7]),
            "turbo_clock": float(row[8]),
            "compatible_ram_type": str(row[9]),
            "price": float(row[10]),
        }

    def map_motherboard(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "socket": str(row[3]),
            "chipset": str(row[4]),
            "ram_slots": int(row[5]),
            "max_ram_frequency": int(row[6]),
            "form_factor": str(row[7]),
            "ram_type": str(row[8]),
            "price": float(row[9]),
        }

    def map_ram(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "capacity": int(row[3]),
            "frequency": int(row[4]),
            "ram_type": str(row[5]),
            "kit_count": int(row[6]),
            "price": float(row[7]),
        }

    def map_psu(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "power": int(row[3]),
            "certificate": str(row[4]),
            "form_factor": str(row[5]),
            "modularity": bool(row[6]),
            "price": float(row[7]),
        }

    def map_case(row: tuple) -> dict:
        return {
            "id": int(row[0]),
            "model_name": str(row[1]),
            "manufacturer": str(row[2]),
            "form_factor": str(row[3]),
            "glass_side_panel": bool(row[4]),
            "included_fans": int(row[5]),
            "price": float(row[6]),
        }

    return {
        "gpu": [map_gpu(row) for row in services.pc_build_service.list_components("GPU")],
        "cpu": [map_cpu(row) for row in services.pc_build_service.list_components("CPU")],
        "motherboard": [map_motherboard(row) for row in services.pc_build_service.list_components("Motherboard")],
        "ram": [map_ram(row) for row in services.pc_build_service.list_components("RAM")],
        "psu": [map_psu(row) for row in services.pc_build_service.list_components("PSU")],
        "pc_case": [map_case(row) for row in services.pc_build_service.list_components("PC_Case")],
    }
