from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_role import ResponseCreateUser, UserCreate, UserCreateResponse, Role, User

router = APIRouter()

@router.post(
    "/register",
    response_model=ResponseCreateUser,
    responses={
        409: {
            "description": "The user already exists"
        }
    },
)
def register(user: UserCreate, session: AsyncSession = Depends(get_db)) -> dict[str, UserCreateResponse]:
    user = add_user(
        session=session, **user.model_dump()
    )
    if not user:
        raise HTTPException(
            409,
            "username or email already exists",
        )
    user_response = UserCreateResponse(
        username=user.username, email=user.email
    )
    return {
        "message": "user created",
        "user": user_response,
    }

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)

def add_user(
        session: AsyncSession,
        username: str,
        password: str,
        email: str,
        role: Role = Role.basic,
) -> User | None:
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        return
    return db_user

async def get_user(session: AsyncSession, username_or_email: str) -> User | None:
    try:
        validate_email(username_or_email)
        query_filter = User.email
    except EmailNotValidError:
        query_filter = User.username
    result = await session.execute(select(User).where(query_filter == username_or_email))
    return result.scalar_one_or_none()