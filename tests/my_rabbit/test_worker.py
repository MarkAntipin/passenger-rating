import json

import pika

from my_rabbit import Worker, Message


class _MockMethod:
    delivery_tag = 1


class _TestWorker(Worker):
    def perform(self, message: Message):
        ...


class _TestWorkerError(Worker):
    def perform(self, message: Message):
        raise Exception('error')


def test_init(connection):
    w = _TestWorker(connection=connection)

    assert w.queue == '_TestWorker'
    assert w.name == '_TestWorker'
    assert w.xq_queue == '_TestWorker.XQ'
    assert w.dq_queue == '_TestWorker.DQ'

    assert w.channel.exchange_declare.called is True
    assert w.channel.queue_declare.call_count == 3
    assert w.channel.queue_bind.call_count == 2
    assert w.channel.basic_qos.called is True


def test_perform(connection):
    w = _TestWorker(connection=connection)
    payload = {'hello': 1}
    bytes_payload = json.dumps(payload)
    w._perform(
        ch=None,
        properties=pika.BasicProperties(headers={'current_retries': 0}),
        method=_MockMethod(),
        body=bytes_payload
    )
    assert w.current_message.payload == payload
    assert w.channel.basic_ack.called is True


def test_perform_error(connection):
    w = _TestWorkerError(connection=connection)
    payload = {'hello': 1}
    bytes_payload = json.dumps(payload)

    w._perform(
        ch=None,
        properties=pika.BasicProperties(headers={'current_retries': 0}),
        method=_MockMethod(),
        body=bytes_payload
    )

    assert w.current_message.current_retries == 1
