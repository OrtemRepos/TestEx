from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model import User
from src.schema import UserCreate, UserRead


class AbstractRepository(ABC):
    @staticmethod
    @abstractmethod
    async def get(user_id: UUID, session: AsyncSession) -> User | None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def get_by_email(email: str, session: AsyncSession) -> User | None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def add(user: UserCreate, session: AsyncSession) -> UUID:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def list(session: AsyncSession) -> list[User]:
        raise NotImplementedError


class UserRepository(AbstractRepository):
    @staticmethod
    async def get(user_id: UUID, session: AsyncSession) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        UserRead.model_validate(user, from_attributes=True)
        return user

    @staticmethod
    async def get_by_email(email: str, session: AsyncSession) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        UserRead.model_validate(user, from_attributes=True)
        return user

    @staticmethod
    async def add(user: UserCreate, session: AsyncSession) -> UUID:
        user_model = User(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
        )
        session.add(user_model)
        await session.flush()
        return user_model.user_id

    @staticmethod
    async def list(session: AsyncSession) -> list[User]:
        stmt = select(User)
        result = await session.execute(stmt)
        return list(result.scalars().all())
