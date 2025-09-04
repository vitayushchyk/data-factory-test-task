from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings

engine = create_async_engine(
    url=settings.db_connection_uri,
    echo=settings.echo_query,
    future=True,
)


Base = declarative_base()


async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_maker() as session:
        yield session
