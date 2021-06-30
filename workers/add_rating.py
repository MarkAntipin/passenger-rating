from my_rabbit import (
    Worker, Message, get_connection, ConnectionType
)


class AddRating(Worker):
    def perform(self, message: Message):
        print('!' * 100)
        print(message.payload)
        print('!' * 100)


def run():
    connection = get_connection(conn_type=ConnectionType.CONSUMER)
    worker = AddRating(connection=connection)
    worker.consume()


if __name__ == '__main__':
    run()
