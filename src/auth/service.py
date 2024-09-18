import secrets
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import config
from src.auth.schema.response import AccessTokenResponse
from src.auth.transport import RedisTransport
from src.auth.util import (
    create_jwt_token,
    decrypt_token,
    encrypt_token,
    get_password_hash,
    verify_jwt_token,
    verify_password,
)
from src.repository import AbstractRepository
from src.schema import UserCreate, UserRead

redis_transport = RedisTransport()


class UserManager:
    def __init__(
        self,
        db: AbstractRepository,
    ) -> None:
        self.db = db
        self.transpot = redis_transport

    async def create_user(
        self, user: UserCreate, session: AsyncSession
    ) -> UUID:
        user_check = await self.db.get_by_email(user.email, session)
        print(user_check)
        if user_check is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user.email=} already registered",
            )

        user.password = get_password_hash(user.password)
        user_uuid = await self.db.add(user, session)
        await session.commit()

        return user_uuid

    async def accses_token(
        self,
        form_data: OAuth2PasswordRequestForm,
        session: AsyncSession,
        agent: str,
    ) -> AccessTokenResponse:
        user = await self.db.get_by_email(form_data.username, session)
        if user is None or not verify_password(
            form_data.password, user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        refresh_token = secrets.token_urlsafe(64)
        key = encrypt_token(refresh_token)
        token = create_jwt_token(user.user_id, agent, key)
        expire_second = config.refresh_token_life_time

        await self.transpot.set(
            user_id=str(user.user_id),
            agent=agent,
            token=refresh_token,
            expire_time=expire_second,
        )

        return AccessTokenResponse(
            access_token=token.access_token,
            expires_at=token.payload.exp,
            refresh_token_expires_at=expire_second,
        )

    async def refresh(self, token: str, agent: str) -> AccessTokenResponse:
        payload = verify_jwt_token(token, agent)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        user_id = payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        refresh_token = await self.transpot.get(user_id, payload.ag)

        if refresh_token is None or refresh_token != decrypt_token(payload.ks):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        refresh_token = secrets.token_urlsafe(64)

        crypt_key = encrypt_token(refresh_token)

        await self.transpot.set(user_id, refresh_token, agent)
        access_token = create_jwt_token(UUID(user_id), payload.ag, crypt_key)

        return AccessTokenResponse(
            access_token=access_token.access_token,
            expires_at=access_token.payload.exp,
            refresh_token_expires_at=config.refresh_token_life_time,
        )

    async def check_token(
        self,
        token: str,
        agent: str,
        session: AsyncSession,
        prefix: str = "auth",
        credentials_exception=HTTPException(  #  noqa: B008
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    ) -> UserRead:
        payload = verify_jwt_token(token, agent)
        username: str = payload.sub
        if username is None:
            raise credentials_exception
        user = await self.db.get(UUID(username), session)
        if user is None:
            raise credentials_exception
        refresh_token = await self.transpot.get(username, agent)
        if refresh_token is None or refresh_token != decrypt_token(payload.ks):
            raise credentials_exception
        return UserRead.model_validate(user, from_attributes=True)

    async def logout(self, user: UserRead) -> None:
        await self.transpot.delete(str(user.user_id))

    async def get_current_user(
        self, token: str, agent: str, session: AsyncSession
    ) -> UserRead:
        token_payload = verify_jwt_token(token, agent)

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

        return UserRead.model_validate(user, from_attributes=True)
