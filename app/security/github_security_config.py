import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_role import User
from app.services.user_services import UserService

GITHUB_CLIENT_ID = "Ov23lifROeiYNNoXSe2I"
GITHUB_CLIENT_SECRET = ""
GITHUB_REDIRECT_URI = "http://localhost:8000/v1/github/auth/token"
GITHUB_AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"


async def resolve_github_token(
    access_token: str = Depends(OAuth2()),
    session: AsyncSession = Depends(get_db),
) -> User:
    user_response = httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": access_token},
        verify=False,
    ).json()
    username = user_response.get("login", " ")
    user = await UserService.find_by_username_or_email(session, username)
    if not user:
        email = user_response.get("email", " ")
        user = await UserService.find_by_username_or_email(session, email)
    # Process user_response to log
    # the user in or create a new account
    if not user:
        raise HTTPException(status_code=403, detail="Token not valid")
    return user
