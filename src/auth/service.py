from uuid import UUID

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.util import (
    create_jwt_token,
    get_password_hash,
    verify_jwt_token,
    verify_password,
)
from src.repository import AbstractRepository, redis_repository
from src.schema import UserCreate, UserRead


class UserManager:
    def __init__(
        self,
        db: AbstractRepository,
        token_lifetime: int | None = None,
        token_refresh_lifetime: int | None = None,
    ) -> None:
        self.db = db
        self.transpot = redis_repository
        self.token_lifetime = token_lifetime
        self.token_refresh_lifetime = token_refresh_lifetime

    async def create_user(
        self, user: UserCreate, session: AsyncSession
    ) -> UUID:
        user_check = await self.db.get_by_email(user.email, session)
        print(user_check)
        if user_check is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user.password = get_password_hash(user.password)
        user_uuid = await self.db.add(user, session)
        await session.commit()

        return user_uuid

    async def login(
        self, form_data: OAuth2PasswordRequestForm, session: AsyncSession
    ) -> UserRead:
        user = await self.db.get_by_email(form_data.username, session)
        if user is None or not verify_password(
            form_data.password, user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        if self.token_lifetime is not None:
            token = create_jwt_token(user.user_id, self.token_lifetime)
            await self.transpot.set(token, self.token_lifetime)
        else:
            token = create_jwt_token(user.user_id)
            await self.transpot.set(token)

        return UserRead.model_validate(user, from_attributes=True)

    async def refresh(
        self, prefix: str, email: str, session: AsyncSession
    ) -> None:
        user = await self.db.get_by_email(email, session)
        if user is None:
            return None

        token = create_jwt_token(user.user_id)
        token.payload.iss = prefix
        await self.transpot.set(token)
        return None

    async def check_token(
        self,
        token: str,
        session: AsyncSession,
        prefix: str = "auth",
        credentials_exception=HTTPException(  #  noqa: B008
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    ) -> UserRead:
        payload = verify_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await self.db.get(UUID(username), session)
        if user is None:
            raise credentials_exception
        return UserRead.model_validate(user, from_attributes=True)

    async def logout(self, user: UserRead) -> None:
        await self.transpot.delete(user.user_id)

    async def get_current_user(
        self, token: str, session: AsyncSession
    ) -> UserRead:
        token_payload = verify_jwt_token(token)

        if token_payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user = await self.db.get(UUID(token_payload.sub), session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        redis_token = await self.transpot.get(user.user_id)
        if (
            redis_token is None
            or verify_jwt_token(redis_token.access_token) != token_payload
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return UserRead.model_validate(user, from_attributes=True)
