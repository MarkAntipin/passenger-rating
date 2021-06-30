from enum import Enum, unique

import pika
import aio_pika

from my_rabbit.config import RabbitConfig, get_config


@unique
class ConnectionSyncType(Enum):
    SYNC = 'sync'
    ASYNC = 'async'


_CONNECTIONS = {
    ConnectionSyncType.SYNC: {},
    ConnectionSyncType.ASYNC: {},
}


@unique
class ConnectionType(Enum):
    PUBLISHER = 'publisher'
    CONSUMER = 'consumer'


def get_connection(
        config: RabbitConfig = None,
        conn_type: ConnectionType = ConnectionType.PUBLISHER
) -> pika.BlockingConnection:
    """
     Get rabbit connection by connection type (`publisher` or `consumer`)
     Connection will be created with `config` param
     or it will use config that has been set with `set_config()`
     or will use default config
    """
    if config is None:
        config = get_config()
    conn = _CONNECTIONS[ConnectionSyncType.SYNC].get((conn_type, config))
    if conn is None:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=config.credentials,
                host=config.host,
                virtual_host=config.virtualhost,
                port=config.port
            ))
        _CONNECTIONS[ConnectionSyncType.SYNC][(conn_type, config)] = conn
    return conn


async def get_async_connection(
        config: RabbitConfig = None,
        conn_type: ConnectionType = ConnectionType.PUBLISHER
):
    if config is None:
        config = get_config()
    conn = _CONNECTIONS[ConnectionSyncType.ASYNC].get((conn_type, config))
    if conn is None:
        conn = await aio_pika.connect(**config.dict())
    return conn


def pop_connection(
        sync_con_type: ConnectionSyncType,
        conn_type: ConnectionType,
        config: RabbitConfig = None
):
    if config is None:
        config = get_config()
    _CONNECTIONS[sync_con_type].pop((conn_type, config), None)
