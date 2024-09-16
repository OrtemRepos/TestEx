from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_superuser: bool = False
    is_active: bool = True


class UserRead(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool
    is_active: bool
    created_at: datetime
    update_at: datetime | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str 
    is_superuser: bool = False
    is_active: bool = True