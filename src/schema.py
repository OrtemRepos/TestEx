from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    disabled: bool