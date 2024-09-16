from src.config import config
from src.auth.config import config as auth_config
import redis


redis_connect = redis.asyncio.from_url(
        url=config.REDIS_URL, username=config.REDIS_USER,
        password=config.REDIS_PASSWORD
)

async def get(key: str) -> str:
    return await redis_connect.get(key)

async def set(key: str, value: str) -> None:
    await redis_connect.set(key, value, ex=auth_config.token_life_time)


