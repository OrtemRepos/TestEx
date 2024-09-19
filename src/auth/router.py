from typing import Annotated

from fastapi import APIRouter, Body, Request, status
from pydantic import EmailStr

from src.auth.schema.response import AccessTokenResponse
from src.dependencies import (
    CurrentUserDep,
    OAuth2FormDep,
    SessionDep,
    UserManagerDep,
)
from src.schema import HTTPResponse, UserCreate, UserRead

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    request: Request,
    user_manager: UserManagerDep,
    session: SessionDep,
) -> HTTPResponse:
    result = await user_manager.create_user(user, request, session)
    return result


@auth_router.post(
    "/access-token",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def token(
    request: Request,
    user_manager: UserManagerDep,
    session: SessionDep,
    form_data: OAuth2FormDep,
) -> AccessTokenResponse:
    return await user_manager.accses_token(form_data, session, request)


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    session: SessionDep,
    user_manager: UserManagerDep,
    user: CurrentUserDep,
) -> HTTPResponse:
    user_model, token = user

    res = await user_manager.logout(user_model, request)
    return res


@auth_router.post(
    "/request-forgot-password", status_code=status.HTTP_202_ACCEPTED
)
async def forgot_password(
    user_manager: UserManagerDep,
    email: Annotated[EmailStr, Body()],
    session: SessionDep,
    request: Request,
) -> HTTPResponse:
    user_model = await user_manager.db.get_by_email(email, session)
    if user_model is None:
        return HTTPResponse(status="success")
    res = await user_manager.forgot_password_token(
        UserRead.model_validate(user_model, from_attributes=True), request
    )

    return res


@auth_router.post("/verification", status_code=status.HTTP_202_ACCEPTED)
async def verification(
    user_manager: UserManagerDep, user: CurrentUserDep, request: Request
) -> HTTPResponse:
    user_model, token = user
    await user_manager.check_refresh_token(token)
    res = await user_manager.verification_token(user_model, request)
    return res


@auth_router.get("/protected")
async def protected(
    user_manager: UserManagerDep,
    user: CurrentUserDep,
) -> HTTPResponse:
    user_model, token = user
    await user_manager.check_refresh_token(token)

    return HTTPResponse(status="success", detail=[user_model])
