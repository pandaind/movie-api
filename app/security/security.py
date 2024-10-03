from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_role import User
from app.services.user_services import pwd_context, UserService


async def authenticate_user(session: AsyncSession, username_or_email: str, password: str) -> User | None:
    user = await UserService.get_user(session, username_or_email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return
    return user


SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, scopes: list[str]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "scopes": scopes})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


async def decode_access_token(token: str, db_session: AsyncSession, required_scopes: list[str]) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes", [])
    except JWTError:
        return
    if not username or not all(scope in token_scopes for scope in required_scopes):
        return
    user = await UserService.get_user(db_session, username)
    user.scopes = token_scopes
    return user
