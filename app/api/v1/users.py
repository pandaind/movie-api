from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_role import ResponseCreateUser, UserCreate, UserCreateResponse, User
from app.services.user_services import UserService

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
