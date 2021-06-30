import logging

from sqlalchemy.engine import Connection
from fastapi import APIRouter, status, Depends, Path, Response
import pika

from app.models import AddRating, AddRatingResponse, GetRatingResponse
from app.database import get_db_conn, rating, get_rating_from_cursor
from my_rabbit import get_async_connection, Message, ConnectionType

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_rabbit_conn_factory():
    return await get_async_connection(config=None, conn_type=ConnectionType.PUBLISHER)


@router.post(
    '',
    description='Водитель ставит оценку пассажиру',
    response_model=AddRatingResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def add_rating(
    payload: AddRating,
    rabbit_conn: pika.BlockingConnection = Depends(get_rabbit_conn_factory)
):
    logger.info(f'Get request on `add_rating` with params: {payload.dict()}')
    message = Message(payload=payload.dict())
    async with rabbit_conn.channel() as channel:
        await message.async_publish(channel=channel, queue='AddRating')
    return AddRatingResponse(message='queued')


@router.get(
    '/{clientId}',
    description='Получить оценку пассажира',
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_200_OK: {'model': GetRatingResponse},
    }
)
def get_rating(
    client_id: int = Path(..., alias='clientId', ge=0),
    conn: Connection = Depends(get_db_conn)
):
    logger.info(f'Get request on `get_rating` with client_id: {client_id}')
    curr = conn.execute(
        rating.select().where(
            rating.c.client_id == client_id
        )
        .with_only_columns([rating.c.id, rating.c.rating, rating.c.client_id])
    )
    res = get_rating_from_cursor(curr)
    if res is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return GetRatingResponse(rating=res['rating'], clientId=res['client_id'])
