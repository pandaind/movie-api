from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_role import User, UserCreate

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)


class UserService:

    @classmethod
    async def add_user(cls, session: AsyncSession, user: User) -> UserCreate | None:
        hashed_password = pwd_context.hash(user.hashed_password)
        add_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        session.add(add_user)
        try:
            await session.commit()
            await session.refresh(add_user)
        except IntegrityError:
            await session.rollback()
            return
        return add_user

    @classmethod
    async def get_user(cls, session: AsyncSession, username_or_email: str) -> User | None:
        try:
            validate_email(username_or_email)
            query_filter = User.email
        except EmailNotValidError:
            query_filter = User.username
        result = await session.execute(select(User).where(query_filter == username_or_email))
        return result.scalar_one_or_none()
