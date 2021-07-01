from my_rabbit.connection import (
    pop_connection,
    ConnectionType, ConnectionSyncType
)
from my_rabbit.connection import _CONNECTIONS


def test_get_connection(connection):
    assert len(_CONNECTIONS[ConnectionSyncType.SYNC]) == 1


def test_pop_connection(connection):
    pop_connection(
        conn_type=ConnectionType.PUBLISHER,
        sync_con_type=ConnectionSyncType.SYNC
    )
    assert len(_CONNECTIONS[ConnectionSyncType.SYNC]) == 0
