import json

from my_rabbit import Message


def _create_message(payload=None):
    payload = payload or {'hello': 1}
    properties = {'hello': 1}
    return Message(
        payload=payload,
        properties=properties,
        max_retries=4,
    )


def test_init():
    payload = {'hello': 1}
    m = _create_message(payload)
    assert m.payload == payload
    assert m.properties == {'hello': 1, 'current_retries': 0}
    assert m.max_retries == 4
    assert m.is_failed is False


def test_from_bytes():
    payload = {'hello': 1}
    bytes_payload = json.dumps(payload)
    m = Message.from_bytes(
        body=bytes_payload,
        max_retries=4,
    )
    assert m.payload == payload
    assert 'current_retries' in m.properties


def test_publish(connection):
    m = _create_message()
    queue = 'test'
    with connection.channel() as channel:
        m.publish(channel=channel, queue=queue)

    assert channel.basic_publish.called is True
    assert channel.basic_publish.call_args.kwargs['routing_key'] == queue
    assert channel.basic_publish.call_args.kwargs['body'] == m.message_body


def test_drop(connection):
    m = _create_message()
    xq_queue = 'test.xq'
    traceback = 'error'
    with connection.channel() as channel:
        m.drop(channel=channel, xq_queue=xq_queue, traceback=traceback)

    assert channel.basic_publish.called is True
    assert channel.basic_publish.call_args.kwargs['routing_key'] == xq_queue
    assert m.is_failed is True
    assert m.traceback == traceback


def test_ack(connection):
    m = _create_message()
    with connection.channel() as channel:
        m.ack(channel=channel)

    assert channel.basic_ack.called is True


def test_requeue(connection):
    m = _create_message()
    xq_queue = 'test.xq'
    dq_queue = 'test.dq'
    with connection.channel() as channel:
        for i in range(1, m.max_retries):
            m.requeue(channel=channel, xq_queue=xq_queue, dq_queue=dq_queue)
            assert m.current_retries == i
            assert channel.basic_publish.called is True

            if m.max_retries > i:
                assert channel.basic_publish.call_args.kwargs['routing_key'] == dq_queue
            else:
                assert channel.basic_publish.call_args.kwargs['routing_key'] == xq_queue
