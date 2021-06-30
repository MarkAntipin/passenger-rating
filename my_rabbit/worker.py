import logging
from abc import ABC, abstractmethod

import pika
from pika.adapters import BlockingConnection
from pika.exceptions import ConnectionClosedByBroker, AMQPConnectionError

from my_rabbit.message import Message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEAD_MESSAGE_TTL = 86400000 * 7
RETRY_TIME = 10 * 1000


class Worker(ABC):

    def __init__(
            self,
            connection: BlockingConnection,
            queue: str = None,
    ):
        self._queue = queue or self.name

        self.connection = connection
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='dlx', exchange_type='direct')
        self._declare_queues()
        self.channel.queue_bind(exchange='amq.direct', queue=self.queue)
        self.channel.queue_bind(exchange='dlx', queue=self.dq_queue)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=self._perform)

        self._current_message = None

    def _declare_queues(self):
        self.channel.queue_declare(
            queue=self.queue,
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': self.dq_queue
            })
        self.channel.queue_declare(
            queue=self.dq_queue,
            durable=True,
            arguments={
                "x-message-ttl": RETRY_TIME,
                'x-dead-letter-exchange': 'amq.direct',
                'x-dead-letter-routing-key': self.queue
            })

        self.channel.queue_declare(
            queue=self.xq_queue,
            durable=True,
            arguments={"x-message-ttl": DEAD_MESSAGE_TTL}
        )

    @property
    def current_message(self) -> Message:
        """Current processed message in self.queue
        """
        return self._current_message

    @property
    def queue(self) -> str:
        """Worker queue name to consume
        """
        return self._queue

    @property
    def xq_queue(self) -> str:
        """Que for storing dead messages for DEAD_MESSAGE_TTL
        """
        return f'{self.queue}.XQ'

    @property
    def dq_queue(self) -> str:
        """Que for requeue messages after RETRY_TIME
        """
        return f'{self.queue}.DQ'

    @property
    def name(self) -> str:
        """Worker name
        """
        return type(self).__name__

    def requeue(self):
        """Shortcut for current_message.requeue
        """
        if self.current_message:
            self.current_message.requeue(
                channel=self.channel,
                dq_queue=self.dq_queue,
                xq_queue=self.xq_queue,
            )

    @property
    def properties(self) -> dict:
        """Shortcut for current_message.properties
        """
        if self.current_message:
            return self.current_message.properties

    @staticmethod
    def _compile_current_message(
            body: bytes, properties: pika.BasicProperties, delivery_tag: str
    ) -> Message:
        """Creates current worker message
        """
        properties = {k: v for k, v in properties.headers.items() if not k.startswith('x-')}
        message = Message.from_bytes(
            body=body,
            properties=properties,
            delivery_tag=delivery_tag
        )
        return message

    def _perform(self, ch, method, properties, body):  # noqa
        """Set current message; run perform and handle handler exceptions
        """
        delivery_tag = method.delivery_tag
        current_message = self._compile_current_message(body, properties, delivery_tag)
        self._current_message = current_message

        try:
            self.perform(current_message)
        except Exception as e:
            trace = repr(e)
            logger.error(
                f'{trace}; worker: {self.name}; queue: {self.queue}'
            )
            self.requeue()

        self.channel.basic_ack(delivery_tag=delivery_tag)

    @abstractmethod  # noqa
    def perform(self, message: Message):
        """Perform worker logic
        """

    def consume(self):
        """Start consuming.
        If lost rabbit connection: put message in xq and stop consuming
        If exception occurred: try to requeue message
        """
        while True:
            try:
                self.channel.start_consuming()
                logger.info(
                    f'Start consuming; worker: {self.name}; queue: {self.queue}'
                )
            except KeyboardInterrupt:
                break

            except (ConnectionClosedByBroker, AMQPConnectionError):
                logger.error('Do not have rabbit connection')
                self.current_message.ack(channel=self.channel)
                break

        self.channel.stop_consuming()
        logger.info('Stop consuming')
