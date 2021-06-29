from enum import Enum, unique

import pika

from my_rabbit.config import RabbitConfig, get_config


_CONNECTIONS = {}


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
    conn = _CONNECTIONS.get((conn_type, config))
    if conn is None:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=config.credentials,
                host=config.host,
                virtual_host=config.virtualhost,
                port=config.port
            ))
        _CONNECTIONS[(conn_type, config)] = conn
    return conn
