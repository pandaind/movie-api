from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import get_db
from app.models.user_role import User, UserCreateResponse, UserRole
from app.security.github_security_config import resolve_github_token
from app.security.model import Token
from app.security.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_premium_user,
)

router = APIRouter()


async def read_user(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return {
        "description": f"{user.username} authorized",
    }


@router.get(
    "/users/me",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authorized"},
        status.HTTP_200_OK: {"description": "username authorized"},
    },
)
async def read_user_me(user: User = Depends(get_current_user)):
    return await read_user(user)


@router.get(
    "/users/premium",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authorized"},
        status.HTTP_200_OK: {"description": "username authorized"},
    },
)
async def read_user_premium(user: User = Depends(get_premium_user)):
    return await read_user(user)


@router.post(
    "/token",
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect username or password"}
    },
    include_in_schema=False,  # hide from swagger
)
async def get_user_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token({"sub": user.username}, [user.role])
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/home",
    responses={status.HTTP_403_FORBIDDEN: {"description": "token not valid"}},
    include_in_schema=False,  # hide from swagger
)
def homepage(user: UserCreateResponse = Depends(resolve_github_token)):
    return {"message": f"logged in {user.username} !"}
