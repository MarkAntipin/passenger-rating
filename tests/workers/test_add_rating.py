from workers.add_rating import AddRating
from my_rabbit import Message
from app.database import rating, rating_log, get_rating_from_cursor


def test_perform(rabbit_connection, db_connection):
    payload = {
        'rating': 3,
        'driver_id': 1,
        'client_id': 1,
    }
    m = Message(payload=payload)
    w = AddRating(connection=rabbit_connection)
    w.perform(message=m)

    r = db_connection.execute(
        rating_log.select().where(rating_log.c.driver_id == payload['driver_id'])
    )
    assert r.fetchone()

    r = db_connection.execute(
        rating.select().where(rating.c.client_id == payload['client_id'])
    )
    r = get_rating_from_cursor(r)
    assert r['rating'] == payload['rating']
