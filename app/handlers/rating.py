from sqlalchemy.engine import Connection
from fastapi import APIRouter, status, Depends, Path, HTTPException

from app.models import AddRating, AddRatingResponse, GetRatingResponse
from app.database import get_db_conn

router = APIRouter()


@router.post(
    '',
    description='Водитель ставит оценку пассажиру',
    response_model=AddRatingResponse,
    status_code=status.HTTP_200_OK
)
def add_rating(
    payload: AddRating,
    conn: Connection = Depends(get_db_conn)
):
    print(payload)
    return AddRatingResponse(message='ok')


@router.get(
    '/{clientId}',
    description='Получить оценку пассажира',
    response_model=GetRatingResponse,
    status_code=status.HTTP_200_OK
)
def get2_rating(
    client_id: int = Path(..., alias='clientId'),
    conn: Connection = Depends(get_db_conn)
):
    a = 1
    return GetRatingResponse(rating=3.6, clientId=client_id)
