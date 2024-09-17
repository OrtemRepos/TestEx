import time
from abc import ABC, abstractmethod
from uuid import UUID

from redis.asyncio.client import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import config as auth_config
from src.auth.schema import JWTToken
from src.config import config
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


class RedisRepository:
    redis = Redis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, user_id: UUID) -> JWTToken | None:
        async with self.redis.client() as conn:
            result = await conn.get(user_id)
            result = JWTToken.model_validate_json(result)
            return result

    async def set(
        self, token: JWTToken, expire_time: int = auth_config.token_life_time
    ) -> None:
        async with self.redis.client() as conn:
            token_json = token.model_dump_json()
            await conn.set(token.payload.sub, token_json, ex=expire_time)

    async def delete(self, user_id: UUID) -> None:
        async with self.redis.client() as conn:
            await conn.delete(user_id)

    async def refresh(
        self,
        user_id: UUID,
        expire_time: int = auth_config.refresh_token_life_time,
    ) -> JWTToken | None:
        async with self.redis.client() as conn:
            token = await conn.get(user_id)

            if token is None or token.payload.exp < int(time.time()):
                return None

            token.payload.exp = int(time.time()) + expire_time
            await conn.expire(user_id, expire_time)
        return token


redis_repository = RedisRepository()
