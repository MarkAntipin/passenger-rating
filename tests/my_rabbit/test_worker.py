import json

import pika

from my_rabbit import Worker, Message


class _MockMethod:
    delivery_tag = 1


class TestWorker(Worker):
    def perform(self, message: Message):
        ...


class TestWorkerError(Worker):
    def perform(self, message: Message):
        raise Exception('error')


def _create_worker(connection):
    return TestWorker(connection=connection)


def test_init(connection):
    w = _create_worker(connection=connection)

    assert w.queue == 'TestWorker'
    assert w.name == 'TestWorker'
    assert w.xq_queue == 'TestWorker.XQ'
    assert w.dq_queue == 'TestWorker.DQ'

    assert w.channel.exchange_declare.called is True
    assert w.channel.queue_declare.call_count == 3
    assert w.channel.queue_bind.call_count == 2
    assert w.channel.basic_qos.called is True


def test_perform(connection):
    w = _create_worker(connection=connection)
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


def test_perform(connection):
    w = TestWorkerError(connection=connection)
    payload = {'hello': 1}
    bytes_payload = json.dumps(payload)

    w._perform(
        ch=None,
        properties=pika.BasicProperties(headers={'current_retries': 0}),
        method=_MockMethod(),
        body=bytes_payload
    )

    assert w.current_message.current_retries == 1
