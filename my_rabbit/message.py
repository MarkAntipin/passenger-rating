import os
import json
import logging
from enum import IntEnum, unique

import pika
from pika.adapters.blocking_connection import BlockingChannel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_RETRIES = 5


@unique
class DeliveryMode(IntEnum):
    NOT_PERSISTENT = 1
    PERSISTENT = 2


class Message:
    def __init__(
            self,
            payload: dict,
            properties: dict = None,
            max_retries: int = MAX_RETRIES,
            delivery_tag: str = None,
    ):
        self._payload = payload
        self.properties = properties or {'current_retries': 0}

        self._max_retries = max_retries
        self._delivery_tag = delivery_tag
        self._is_failed = False
        self._traceback = None

    def publish(
            self,
            channel: BlockingChannel,
            queue: str,
            content_type: str = 'application/json',
            create_queue: bool = False
    ):
        """Publish message in queue

        :param BlockingChannel channel: Channel for rabbit connection
        :param str queue: Queue to publish in
        :param str content_type: Content type of message body
        :param bool create_queue: Create queue if it is not exists
        """
        if create_queue:
            channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=self.message_body,
            properties=pika.BasicProperties(
                headers=self.properties,
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type=content_type
            ))

    def requeue(self, channel: BlockingChannel, dq_queue: str, xq_queue: str):
        """Requeue message. Put it in dq and restarts every RETRY_TIME
        after self.max_retries put in xq

        :param BlockingChannel channel: Channel for rabbit connection
        :param str dq_queue: Queue retry
        :param str xq_queue: Queue to store dead messages
        """
        if self.properties['current_retries'] >= self._max_retries:
            logger.info('Sending message into XQ')
            self.drop(channel=channel, xq_queue=xq_queue)
            return
        self.properties['current_retries'] += 1
        logger.info(
            'Retrying message',
            extra={'current_retries': self.properties['current_retries']}
        )
        self.publish(channel=channel, queue=dq_queue)

    def drop(self, channel: BlockingChannel, xq_queue: str, traceback: str = None):
        """Put message in xq wher it will be stored for DEAD_MESSAGE_TTL

        :param BlockingChannel channel: Channel for rabbit connection
        :param str xq_queue: Queue to store dead messages
        :param str traceback: Traceback if exception occurred
        """
        self._is_failed = True
        self._traceback = traceback
        self.publish(channel=channel, queue=xq_queue)

    def ack(self, channel: BlockingChannel):
        """Ack message

        :param BlockingChannel channel: Channel for rabbit connection
        """
        channel.basic_ack(delivery_tag=self.delivery_tag)

    @property
    def is_failed(self) -> bool:
        """ Is message failed (in xq)
        """
        return self._is_failed

    @property
    def traceback(self) -> str:
        """ Traceback for failed messages
        """
        return self._traceback

    @property
    def delivery_tag(self) -> str:
        return self._delivery_tag

    @property
    def payload(self) -> dict:
        """ Message payload
        """
        return self._payload

    @staticmethod
    def _payload_from_body(body: bytes) -> dict:
        """ Load message payload from bytes
        """
        payload = json.loads(body)
        return payload

    @property
    def message_body(self) -> bytes:
        """ Dumps message payload into bytes
        """
        body_dict = {'payload': self.payload, 'properties': self.properties}
        return json.dumps(body_dict).encode()

    @classmethod
    def from_bytes(
            cls,
            body: bytes,
            max_retries: int = MAX_RETRIES,
            delivery_tag: str = None
    ):
        payload_with_properties = cls._payload_from_body(body)
        payload = payload_with_properties.pop('payload', None)
        properties = payload_with_properties.pop('properties', None)
        if payload is None:
            payload = payload_with_properties

        return cls(
            payload=payload,
            properties=properties,
            max_retries=max_retries,
            delivery_tag=delivery_tag
        )

    @classmethod
    def from_dict(
            cls,
            payload: dict,
            properties: dict = None,
            max_retries: int = MAX_RETRIES,
            delivery_tag: str = None
    ):
        return cls(
            payload=payload,
            properties=properties,
            max_retries=max_retries,
            delivery_tag=delivery_tag
        )
