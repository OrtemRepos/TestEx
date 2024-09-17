from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import UserManager
from src.database import get_session
from src.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def async_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_user_manager() -> AsyncGenerator[UserManager, None]:
    yield UserManager(db=UserRepository())


async def get_current_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    return token
