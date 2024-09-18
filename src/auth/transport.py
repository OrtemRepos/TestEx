import secrets

from redis.asyncio.client import Redis

from src.auth.config import config as auth_config
from src.config import config


class RedisTransport:
    redis = Redis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, user_id: str, agent: str) -> str | None:
        async with self.redis.client() as conn:
            result = await conn.get(f"{agent}_{user_id}")
            return result

    async def set(
        self,
        user_id: str,
        agent: str,
        token: str,
        expire_time: int = auth_config.refresh_token_life_time,
    ):
        async with self.redis.client() as conn:
            await conn.set(f"{agent}_{user_id}", token, expire_time)
            print(f"set {user_id} {token} {expire_time}")

    async def delete(self, user_id: str) -> None:
        async with self.redis.client() as conn:
            await conn.delete(user_id)

    async def refresh(
        self,
        user_id: str,
        expire_time: int = auth_config.refresh_token_life_time,
    ) -> str | None:
        async with self.redis.client() as conn:
            token = await conn.get(user_id)

            if token is None:
                return token

            token = secrets.token_urlsafe(64)
            await conn.set(user_id, token, expire_time)
            return token
