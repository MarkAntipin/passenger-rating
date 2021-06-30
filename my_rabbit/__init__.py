"""
 Это моя обертка над pika для работы с ребитом;
 Я пока не использую ее нигде в реальных проектах
 Было бы классно (если у вас есть время) сделать ревью кода который находится в этом модуле и дать любые комментарии
"""


from .worker import Worker
from .message import Message
from .connection import get_connection, ConnectionType


__all__ = [
    'Worker',
    'Message',
    'get_connection',
    'ConnectionType',
]
