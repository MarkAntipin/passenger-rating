from datetime import datetime as dt

from sqlalchemy import (
    Table, MetaData, Column, create_engine,
    Integer, DateTime, Float
)
from sqlalchemy.engine import Connection

from settings import settings

metadata = MetaData()

rating = Table(
    'rating',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, index=True),
    Column('client_id', Integer, index=True, unique=True),
    Column('rating', Float, default=None, nullable=True),

    Column('created_at', DateTime, default=dt.utcnow),
    Column('updated_at', DateTime, default=dt.utcnow, onupdate=dt.utcnow)
)

rating_log = Table(
    'rating_log',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, index=True),
    Column('client_id', Integer, index=True),
    Column('driver_id', Integer, index=True),
    Column('rating', Float),

    Column('created_at', DateTime, default=dt.utcnow),
    Column('updated_at', DateTime, default=dt.utcnow, onupdate=dt.utcnow)
)


engine = create_engine(
    settings.pg_url(), echo=True
)


def generate_schemas():
    metadata.drop_all(engine)
    metadata.create_all(engine)


def get_db_conn() -> Connection:
    with engine.begin() as conn:
        yield conn
