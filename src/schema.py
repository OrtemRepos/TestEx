from abc import ABC
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    first_name: str
    email: EmailStr
    password: str


class Identifiable(BaseModel, ABC):
    id: UUID
    create_at: datetime = datetime.utcnow()
    update_at: datetime | None = None


class UserRead(Identifiable):
    email: EmailStr
    first_name: str


class UserUpdate(Identifiable):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: Literal["success", "fail"] = "success"


class HTTPResponse(BaseResponse):
    detail: list | None = None
