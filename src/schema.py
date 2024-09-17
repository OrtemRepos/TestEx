from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    first_name: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: str
    created_at: datetime
    update_at: datetime | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str
    created_at: datetime
    update_at: datetime
