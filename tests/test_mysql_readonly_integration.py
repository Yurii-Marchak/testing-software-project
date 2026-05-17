import os

import pytest

from app.config import load_database_config
from app.infrastructure.database import create_connection
from app.repositories.client_repository import ClientRepository
from app.repositories.component_repository import ComponentRepository


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1",
    reason="Set RUN_MYSQL_INTEGRATION=1 to run read-only MySQL integration checks.",
)


def test_clients_repository_can_read_real_mysql():
    config = load_database_config()
    connection = create_connection(config)
    assert connection is not None
    try:
        rows = ClientRepository(connection).list_all()
        assert isinstance(rows, tuple)
    finally:
        connection.close()


def test_component_repository_can_read_real_mysql():
    config = load_database_config()
    connection = create_connection(config)
    assert connection is not None
    try:
        rows = ComponentRepository(connection).list_all("GPU")
        assert isinstance(rows, tuple)
    finally:
        connection.close()

