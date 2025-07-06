from email_validator import EmailNotValidError, validate_email
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from app.models.user_role import User, UserCreate, Profile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    @classmethod
    async def create_user(cls, session: AsyncSession, user: User) -> UserCreate | None:
        hashed_password = pwd_context.hash(user.hashed_password)
        user.hashed_password = hashed_password
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            return
        return user

    @classmethod
    async def find_by_username_or_email(
        cls, session: AsyncSession, username_or_email: str
    ) -> User | None:
        try:
            validate_email(username_or_email)
            query_filter = User.email
        except EmailNotValidError:
            query_filter = User.username
        result = await session.execute(
            select(User).where(query_filter == username_or_email)
        )
        return result.scalar_one_or_none()

    # Use join for filtering and sorting based on related tables.
    # Use joinedload for eager loading related objects to avoid additional queries.
    @classmethod
    async def _get_user_with_options(
        cls, session: AsyncSession, user_id: int, *options
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        if options:
            statement = statement.options(*options)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_with_profile(
        cls, session: AsyncSession, user_id: int
    ) -> User | None:
        return await cls._get_user_with_options(
            session, user_id, joinedload(User.profile)
        )

    @classmethod
    async def get_user_with_profile_join(
        cls, session: AsyncSession, user_id: int
    ) -> User | None:
        # It's important to note that options like join() cannot be passed as
        # arguments to the options() method of a query.
        # Therefore, this method cannot use the _get_user_with_options helper.
        result = await session.execute(
            select(User)
            .join(User.profile)
            .options(load_only(User.username, User.email))  # User.profile removed
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_with_ony_bio(
        cls, session: AsyncSession, user_id: int
    ) -> User | None:
        return await cls._get_user_with_options(
            session, user_id, joinedload(User.profile).load_only(Profile.bio)
        )
