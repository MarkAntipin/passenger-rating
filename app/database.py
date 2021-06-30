from datetime import datetime as dt
from typing import List

from sqlalchemy import (
    Table, MetaData, Column, create_engine,
    Integer, DateTime, Float
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.cursor import CursorResult

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


def get_rating_from_cursor(c: CursorResult) -> [dict, None]:
    r = c.fetchone()
    if not r:
        return
    return dict(r)


def get_list_rating_from_cursor(c: CursorResult) -> [List[dict], None]:
    r = c.fetchall()
    if not r:
        return
    return [dict(_) for _ in r]
