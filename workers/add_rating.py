from my_rabbit import (
    Worker, Message, get_connection, ConnectionType
)
from app.database import engine, rating, rating_log, get_list_rating_from_cursor
from core.count_rating import count_mean_rating


def add_rating_log(payload: dict, conn):
    conn.execute(
        rating_log.insert()
        .values(**payload)
    )


def get_all_client_rating(client_id: str, conn):
    curr = conn.execute(
        rating_log.select()
        .where(rating_log.c.client_id == client_id)
        .with_only_columns([rating_log.c.driver_id, rating_log.c.rating])
    )

    res = get_list_rating_from_cursor(curr)
    return [r['rating'] for r in res]


def _is_rating_exists(client_id: str, conn) -> bool:
    curr = conn.execute(
        rating.select().where(rating.c.client_id == client_id)
    )
    return bool(curr.fetchone())


def _update_rating(client_id: str, client_rating: float, conn):
    conn.execute(
        rating.update()
        .where(rating.c.client_id == client_id)
        .values(rating=client_rating)
    )


def _insert_taring(client_id: str, client_rating: float, conn):
    conn.execute(
        rating.insert()
        .values(rating=client_rating, client_id=client_id)
    )


def insert_or_update_rating(client_id: str, client_rating: float, conn):
    exists = _is_rating_exists(client_id=client_id, conn=conn)
    if exists:
        _update_rating(client_id=client_id, client_rating=client_rating, conn=conn)
    else:
        _insert_taring(client_id=client_id, client_rating=client_rating, conn=conn)


class AddRating(Worker):
    def perform(self, message: Message):
        payload = message.payload
        client_id = payload['client_id']

        with engine.connect() as conn:
            add_rating_log(payload=payload, conn=conn)

        with engine.begin() as conn:
            rating_list = get_all_client_rating(client_id=client_id, conn=conn)
            client_rating = count_mean_rating(all_ratings=rating_list)
            insert_or_update_rating(client_id=client_id, client_rating=client_rating, conn=conn)


def run():
    connection = get_connection(conn_type=ConnectionType.CONSUMER)
    worker = AddRating(connection=connection)
    worker.consume()
