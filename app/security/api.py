from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import get_db
from app.security.model import Token, oauth2_scheme
from app.security.security import decode_access_token, authenticate_user, create_access_token

router = APIRouter()


@router.get(
    "/users/me",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "User not authorized"
        },
        status.HTTP_200_OK: {
            "description": "username authorized"
        },
    },
)
def read_user_me(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db),
):
    user = decode_access_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return {
        "description": f"{user.username} authorized",
    }


@router.post(
    "/token",
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect username or password"
        }
    },
)
async def get_user_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }