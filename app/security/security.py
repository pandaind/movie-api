from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import get_db
from app.models.user_role import User, UserRole
from app.security.model import oauth2_scheme
from app.services.user_services import UserService, pwd_context


async def authenticate_user(
    session: AsyncSession, username_or_email: str, password: str
) -> User | None:
    user = await UserService.find_by_username_or_email(session, username_or_email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return
    return user


SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, scopes: list[str]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "scopes": scopes})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_access_token(
    token: str, db_session: AsyncSession, required_scopes: list[str]
) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes", [])
    except JWTError:
        return
    if not username or not all(scope in token_scopes for scope in required_scopes):
        return
    user = await UserService.find_by_username_or_email(db_session, username)
    user.scopes = token_scopes
    return user


async def decode_access_token_no_scope(
    token: str, db_session: AsyncSession
) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes", [])
    except JWTError:
        return
    if not username:
        return
    user = await UserService.find_by_username_or_email(db_session, username)
    user.scopes = token_scopes
    user.totp_secret = payload.get("totp_secret")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
    required_role: UserRole = UserRole.basic,
):
    user = await decode_access_token(token, session, [required_role])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return user


async def get_premium_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)
):
    return await get_current_user(token, session, UserRole.premium)


### Credit Card Encryption

key = Fernet.generate_key()
cypher_suite = Fernet(key)


def encrypt_credit_card_info(card_info: str) -> str:
    return cypher_suite.encrypt(card_info.encode()).decode()


def decrypt_credit_card_info(encrypted_card_info: str) -> str:
    return cypher_suite.decrypt(encrypted_card_info.encode()).decode()
