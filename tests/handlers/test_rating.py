from fastapi import status

from app.database import rating


def test_get_rating_no_content(client):
    response = client.get('rating/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_rating(override_db_conn, client, db_connection):
    rating_payload = {'rating': 4.5, 'client_id': 1}
    db_connection.execute(
        rating.insert()
        .values(**rating_payload)
    )

    response = client.get('rating/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'rating': 4.5, 'clientId': 1}
