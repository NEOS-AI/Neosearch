from collections.abc import AsyncGenerator
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import os
from typing import Any, Generator
from urllib.parse import urlparse
import logging


# set up logging config of sqlalchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)


original_conn_string = os.environ.get("PG_CONNECTION_STRING")
if original_conn_string is None or original_conn_string == "":
    raise ValueError("PG_CONNECTION_STRING environment variable is not set.")

original_scheme = urlparse(original_conn_string).scheme + "://"
conn_string = original_conn_string.replace(
    original_scheme, "postgresql+psycopg2://"
)
async_conn_string = original_conn_string.replace(
    original_scheme, "postgresql+asyncpg://"
)

engine = create_engine(
    conn_string,
    echo=True,
)
async_engine = create_async_engine(
    async_conn_string,
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired after commit.
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session
    session.close()

def get_session(engine) -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
    session.close()
