from abc import ABC
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model import User

class AbstractRepository(ABC): ...


class UserRepository(AbstractRepository):
    async def get_by_id(
        self, session: AsyncSession, user_id: UUID
    ) -> User | None:
        try:
            user = await session.get(User, user_id)
            assert user is not None
            UserRead.model_validate(user, from_attributes=True)
            return user
        except UserNotExists:
            print(f"User {user_id} does not exist")
            return None

    @async_start
    async def get_by_email(
        self, session: AsyncSession, email: str
    ) -> User | None:
        try:
            stmt = select(User).where(User.email == email)  # type: ignore
            user = await session.execute(stmt)
            user_result = user.scalars().one()
            UserRead.model_validate(user_result, from_attributes=True)
            return user_result
        except UserNotExists:
            print(f"User {email} does not exist")
            return None

    # @async_start
    async def add(
        self,
        manager: UserManager,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        is_superuser: bool = False,
    ) -> User | None:
        try:
            user = UserCreate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_superuser=is_superuser,
            )
            result = await manager.create(user)
            return result
        except UserAlreadyExists:
            print(f"User {email} already exists")
            return None

    @async_start
    async def list(self, session: AsyncSession) -> list[User]:
        stmt = select(User)
        session_result = await session.execute(stmt)
        user_list = [User(*user) for user in session_result.scalars().all()]  # type: ignore[misc]
        return user_list
