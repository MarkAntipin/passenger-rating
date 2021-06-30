from sqlalchemy.engine import Connection
from fastapi import APIRouter, status, Depends, Path
import pika

from app.models import AddRating, AddRatingResponse, GetRatingResponse
from app.database import get_db_conn, rating
from my_rabbit import get_async_connection, Message, ConnectionType

router = APIRouter()


async def get_rabbit_conn_factory():
    return await get_async_connection(config=None, conn_type=ConnectionType.PUBLISHER)


@router.post(
    '',
    description='Водитель ставит оценку пассажиру',
    response_model=AddRatingResponse,
    status_code=status.HTTP_200_OK
)
async def add_rating(
    payload: AddRating,
    rabbit_conn: pika.BlockingConnection = Depends(get_rabbit_conn_factory)
):
    message = Message(payload=payload.dict())
    async with rabbit_conn.channel() as channel:
        await message.async_publish(channel=channel, queue='AddRating')
    return AddRatingResponse(message='ok')


@router.get(
    '/{clientId}',
    description='Получить оценку пассажира',
    response_model=GetRatingResponse,
    status_code=status.HTTP_200_OK
)
def get_rating(
    client_id: int = Path(..., alias='clientId'),
    conn: Connection = Depends(get_db_conn)
):
    r = conn.execute(
        rating.select().where(
            rating.c.client_id == client_id
        )
        .with_only_columns([rating.c.id, rating.c.rating, rating.c.client_id])
    )
    print(r)
    return GetRatingResponse(rating=3.6, clientId=client_id)
