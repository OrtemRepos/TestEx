from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import config


def new_async_engine() -> AsyncEngine:
    return create_async_engine(
        config.POSTGRES_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30.0,
        pool_recycle=600,
    )


_engine = new_async_engine()
_session_maker = async_sessionmaker(_engine, expire_on_commit=False)


def get_session() -> AsyncSession:
    return _session_maker()
