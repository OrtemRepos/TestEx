from abc import ABC
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model import User
from src.schema import UserRead

class AbstractRepository(ABC): ...
