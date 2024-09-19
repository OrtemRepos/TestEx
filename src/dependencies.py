from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema.token import JWTTokenPayload
from src.auth.service import UserManager
from src.auth.util import verify_jwt_token
from src.database import get_session
from src.repository import UserRepository
from src.schema import UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def async_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(async_get_session)]


async def get_user_manager() -> AsyncGenerator[UserManager, None]:
    yield UserManager(db=UserRepository())


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]


async def get_current_user(
    request: Request, token: TokenDep, session: SessionDep
) -> tuple[UserRead, JWTTokenPayload]:
    token_payload = verify_jwt_token(
        token, agent=request.headers["user-agent"]
    )

    user = await UserRepository.get(UUID(token_payload.sub), session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to access this resource",
        )
    return (UserRead.model_validate(user, from_attributes=True), token_payload)


CurrentUserDep = Annotated[
    tuple[UserRead, JWTTokenPayload], Depends(get_current_user)
]
OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
