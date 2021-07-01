import mock
import pytest
import pika

# from settings import settings
# from app.app import app
from my_rabbit.connection import get_connection


@pytest.fixture()
@mock.patch('my_rabbit.connection.pika.BlockingConnection', mock.MagicMock(spec=pika.BlockingConnection))
def connection():
    return get_connection()


