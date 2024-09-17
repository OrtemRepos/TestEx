from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import UserManager
from src.dependencies import (
    async_get_session,
    get_current_token,
    get_user_manager,
)
from src.schema import UserCreate, UserRead

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UUID)
async def register(
    user: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),  # noqa: B008
    session: AsyncSession = Depends(async_get_session),  # noqa: B008
) -> UUID:
    return await user_manager.create_user(user, session)


@auth_router.post("/access-token", response_model=UserRead)
async def login(
    user_manager: UserManager = Depends(get_user_manager),  # noqa: B008
    session: AsyncSession = Depends(async_get_session),  # noqa: B008
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
) -> UserRead:
    return await user_manager.login(form_data, session)


@auth_router.post("/logout")
async def logout(
    session: AsyncSession = Depends(async_get_session),  # noqa: B008
    user_manager: UserManager = Depends(get_user_manager),  # noqa: B008
    token: str = Depends(get_current_token),  # noqa: B008
) -> None:
    user = await user_manager.check_token(token, session)
    await user_manager.logout(user)

@auth_router.get("/protected")
async def protected(
    user_manager: UserManager = Depends(get_user_manager),  # noqa: B008
    token: str = Depends(get_current_token),  # noqa: B008
    session: AsyncSession = Depends(async_get_session),  # noqa: B008
) -> UserRead:
    print(token)
    return await user_manager.check_token(token, session)
