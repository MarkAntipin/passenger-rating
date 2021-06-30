from fastapi import FastAPI

from app.handlers import rating
from app.database import generate_schemas
from settings import settings
from my_rabbit import get_async_connection, pop_connection, ConnectionType, ConnectionSyncType


async def check_rabbit_connection():
    try:
        conn = await get_async_connection()
    except ConnectionError:
        raise ConnectionError('cant connect to RabbitMQ')
    return conn


async def ping():
    con = await check_rabbit_connection()
    if con.connection.is_closed:
        pop_connection(
            conn_type=ConnectionType.PUBLISHER,
            sync_con_type=ConnectionSyncType.SYNC
        )
        raise ConnectionError('RabbitMQ connection is closed')
    return {'status': 'ok'}


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        on_startup=(generate_schemas,)
    )
    app.include_router(
        router=rating.router,
        tags=['rating management'],
        prefix='/rating',
    )
    app.add_api_route(
        path='/ping',
        endpoint=ping,
        tags=['Health checks']
    )
    return app


app = create_app()
