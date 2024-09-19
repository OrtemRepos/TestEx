import secrets
from uuid import UUID

import cryptography
import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import config
from src.auth.schema.response import AccessTokenResponse
from src.auth.schema.token import JWTTokenPayload
from src.auth.transport import RedisTransport
from src.auth.util import (
    create_jwt_token,
    decrypt_token,
    encrypt_token,
    get_password_hash,
    verify_jwt_token,
    verify_password,
)
from src.email_celery.constant import html_forgot_password_msg, html_verify_msg
from src.email_celery.router import (
    send_forgot_password_email_task,
    send_verification_email_task,
)
from src.email_celery.util import generate_email
from src.repository import AbstractRepository
from src.schema import HTTPResponse, UserCreate, UserRead

redis_transport = RedisTransport()


class UserManager:
    def __init__(
        self,
        db: AbstractRepository,
    ) -> None:
        self.db = db
        self.transpot = redis_transport

    async def check_refresh_token(
        self, token: JWTTokenPayload
    ) -> HTTPResponse:
        refresh_token_cryt = token.ks
        refresh_token = await self.transpot.get(token.sub, token.ag)
        refresh_token_decrypt = decrypt_token(refresh_token_cryt)
        if refresh_token != refresh_token_decrypt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        return HTTPResponse(status="success")

    async def create_user(
        self, user: UserCreate, request: Request, session: AsyncSession
    ) -> HTTPResponse:
        user_check = await self.db.get_by_email(user.email, session)
        print(user_check)
        if user_check is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user.email=} already registered",
            )

        user.password = get_password_hash(user.password)
        user_read = await self.db.add(user, session)
        await session.commit()
        self.after_register(request, user=user_read)
        return HTTPResponse(status="success", detail=[user_read])

    async def accses_token(
        self,
        form_data: OAuth2PasswordRequestForm,
        session: AsyncSession,
        request: Request,
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
        token = create_jwt_token(user.id, request.headers["user-agent"], key)
        expire_second = config.refresh_token_life_time

        await self.transpot.set(
            user_id=str(user.id),
            agent=request.headers["user-agent"],
            token=refresh_token,
            expire_time=expire_second,
        )
        self.after_login(
            request, UserRead.model_validate(user, from_attributes=True)
        )
        return AccessTokenResponse(
            access_token=token.access_token,
            expires_at=token.payload.exp,
            refresh_token_expires_at=expire_second,
        )

    async def refresh(
        self, token: str, request: Request
    ) -> AccessTokenResponse:
        try:
            payload = verify_jwt_token(token, request.headers["user-agent"])
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            id = payload.sub
            if id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )

            refresh_token = await self.transpot.get(id, payload.ag)

            if refresh_token is None or refresh_token != decrypt_token(
                payload.ks
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )

            refresh_token = secrets.token_urlsafe(64)

            crypt_key = encrypt_token(refresh_token)

            await self.transpot.set(
                id, refresh_token, request.headers["user-agent"]
            )
            access_token = create_jwt_token(UUID(id), payload.ag, crypt_key)

        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            ) from e
        except cryptography.fernet.InvalidToken as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials?",
            ) from e

        return AccessTokenResponse(
            access_token=access_token.access_token,
            expires_at=access_token.payload.exp,
            refresh_token_expires_at=config.refresh_token_life_time,
        )

    async def logout(self, user: UserRead, request: Request) -> HTTPResponse:
        await self.transpot.delete(str(user.id))
        self.after_logout(request, user)
        return HTTPResponse(status="success")

    async def forgot_password_token(
        self, user: UserRead, request: Request
    ) -> HTTPResponse:
        numbers = [secrets.choice(range(10)) for _ in range(6)]
        secrets_code = "".join(map(str, numbers))
        await self.transpot.set(
            user_id=str(user.id),
            agent=request.headers["user-agent"],
            token=secrets_code,
            expire_time=300,
            iss="forgot",
        )
        self.after_forgot_password(request, user, secrets_code)
        return HTTPResponse(status="success")

    async def verification_token(
        self, user: UserRead, request: Request
    ) -> HTTPResponse:
        numbers = [secrets.choice(range(10)) for _ in range(6)]
        secrets_code = "".join(map(str, numbers))
        await self.transpot.set(
            user_id=str(user.id),
            agent=request.headers["user-agent"],
            token=secrets_code,
            expire_time=300,
            iss="verify",
        )
        self.after_request_verification(request, user, secrets_code)
        return HTTPResponse(status="success")

    def after_login(self, request: Request, user: UserRead) -> None:
        print("after login")
        print(f"Uset with id {user.id} logged in")

    def after_logout(self, request: Request, user: UserRead) -> None:
        print("after logout")
        print(f"Uset with id {user.id} logged out")

    def after_register(self, request: Request, user: UserRead) -> None:
        print("after register")
        print(f"Uset with id {user.id} registered")

    def after_forgot_password(
        self, request: Request, user: UserRead, token: str
    ) -> None:
        print(f"Uset with id {user.id} forgot password")
        print(token)
        msg = generate_email(
            user_email=user.email,
            token=token,
            html_msg=html_forgot_password_msg,
            subject_msg="Forgot Password",
        )
        send_forgot_password_email_task.delay(user.email, msg.as_string())

    def after_change_password(self, request: Request, user: UserRead) -> None:
        print("after change password")
        print(f"Uset with id {user.id} change password")

    def after_request_verification(
        self, request: Request, user: UserRead, token: str
    ) -> None:
        print(f"Uset with id {user.id} request verification")
        print(token)
        msg = generate_email(
            user_email=user.email,
            token=token,
            html_msg=html_verify_msg,
            subject_msg="Verification",
        )
        send_verification_email_task.delay(user.email, msg.as_string())

    def after_verify_email(self, request: Request, user: UserRead) -> None:
        print("after verify email")
        print(f"Uset with id {user.id} verify email")
