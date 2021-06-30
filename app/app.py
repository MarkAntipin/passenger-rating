from fastapi import FastAPI

from app.handlers import rating
from app.database import generate_schemas
from settings import settings


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

    return app


app = create_app()
