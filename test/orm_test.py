import pytest
import pytest_asyncio
import sqlalchemy
from sqlalchemy import select

from src.database import _engine as engine
from src.database import get_session
from src.model import Base, User


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def refresh_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.asyncio(loop_scope="session")
async def test_add(refresh_db):
    user = User(email="a@a.com", first_name="John", hashed_password="12345678")

    async with get_session() as session:
        session.add(user)
        await session.flush()
        await session.commit()
        assert user


@pytest.mark.asyncio(loop_scope="session")
async def test_get():
    async with get_session() as session:
        stmt = select(User).where(User.email == "a@a.com")
        result = await session.execute(stmt)
        user = result.scalars().one()
        print(user)
        assert user
        assert user.email == "a@a.com"
        assert user.first_name == "John"
        await session.close()


@pytest.mark.asyncio(loop_scope="session")
async def test_exception_create_duplicate():
    user = User(email="a@a.com", first_name="John", hashed_password="12345678")

    async with get_session() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.add(user)
            await session.commit()
            session.add(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_list():
    async with get_session() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        print(users)
        assert type(users) is list


@pytest.mark.asyncio(loop_scope="session")
async def test_complete(refresh_db):
    assert True
