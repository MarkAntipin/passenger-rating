from abc import ABC

import pika

from my_rabbit.connection import get_connection


class RabbitBroker(ABC):
    def __init__(self, connection: pika.BlockingConnection = None):
        self.connection = connection or get_connection()
        self.channel = self.connection.channel()

    def