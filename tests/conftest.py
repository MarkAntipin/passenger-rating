import mock
import pytest
import pika
from fastapi.testclient import TestClient

from app.app import app
from app.database import metadata, get_db_conn, engine
from my_rabbit.connection import get_connection


@pytest.fixture(scope="session")
def tables():
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


def get_db_conn_mock():
    connection = engine.connect()
    return connection


@pytest.fixture()
def db_connection(tables):
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
async def override_db_conn():
    app.dependency_overrides[get_db_conn] = get_db_conn_mock()
    yield
    app.dependency_overrides = {}


@pytest.fixture()
@mock.patch('my_rabbit.connection.pika.BlockingConnection', mock.MagicMock(spec=pika.BlockingConnection))
def rabbit_connection():
    return get_connection()


@pytest.fixture(scope='module')
def client():
    with TestClient(app=app) as client:
        yield client
