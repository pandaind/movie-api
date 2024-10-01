from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import get_db
from app.models.user_role import ResponseCreateUser, UserCreate, UserCreateResponse, User, Role
from app.services.user_services import UserService

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={
        409: {
            "description": "The user already exists"
        }
    },
)
async def register(user: UserCreate, session: AsyncSession = Depends(get_db)) -> dict[str, UserCreateResponse]:
    user = User(username=user.username, email=user.email, hashed_password=user.password)
    user_response = await UserService.add_user(
        session=session, user=user
    )
    if not user_response:
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

@router.post(
    "/register/premium-user",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "The user already exists"
        },
        status.HTTP_201_CREATED: {
            "description": "User created"
        },
    },
)
async def register_premium_user(user: UserCreate,session: AsyncSession = Depends(get_db)):
    user = User(username=user.username, email=user.email, hashed_password=user.password, role=Role.premium)
    user_response = await UserService.add_user(session=session, user=user)
    if not user_response:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "username or email already exists",
        )
    user_response = UserCreateResponse(
        username=user.username,
        email=user.email,
    )
    return {
        "message": "user created",
        "user": user_response,
    }