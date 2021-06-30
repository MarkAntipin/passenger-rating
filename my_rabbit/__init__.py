"""
 Это моя обертка над pika для работы с ребитом;
 Я пока не использую ее нигде в реальных проектах
 Было бы классно (если у вас есть время) сделать ревью кода который находится в этом модуле и дать любые комментарии
"""


from .worker import Worker
from .message import Message
from .connection import (
    get_connection, get_async_connection, ConnectionType, pop_connection, ConnectionSyncType
)
from .config import set_config, get_config, RabbitConfig


__all__ = [
    'Worker',
    'Message',
    'get_connection',
    'get_async_connection',
    'pop_connection',
    'ConnectionType',
    'ConnectionSyncType',
    'set_config',
    'get_config',
    'RabbitConfig'
]
