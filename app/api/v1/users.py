from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from app.db.database import get_db
from app.models.user_role import (
    ResponseCreateUser,
    User,
    UserCreate,
    UserCreateResponse,
    UserRole,
)
from app.security.security import get_current_user
from app.services.user_services import UserService

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={409: {"description": "The user already exists"}},
)
async def register(
    user: UserCreate, session: AsyncSession = Depends(get_db)
) -> dict[str, UserCreateResponse]:
    user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
        role=UserRole(user.role),
    )
    user_response = await UserService.create_user(session=session, user=user)
    if not user_response:
        raise HTTPException(
            409,
            "username or email already exists",
        )
    user_response = UserCreateResponse(username=user.username, email=user.email)
    return {
        "message": "user created",
        "user": user_response,
    }


@router.post("/login")
async def login(
    response: Response,
    user: UserCreateResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    user = await UserService.find_by_username_or_email(session, user.username)

    response.set_cookie(key="fakesession", value=f"{user.id}", httponly=True)
    return {"message": "User logged in successfully"}


@router.post("/logout")
async def logout(
    response: Response,
    _user: UserCreateResponse = Depends(get_current_user),
):
    response.delete_cookie("fakesession")  # Clear session data
    return {"message": "User logged out successfully"}
