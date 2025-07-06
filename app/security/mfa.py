import pyotp
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_role import UserCreateResponse
from app.security.model import oauth2_scheme
from app.security.security import decode_access_token, decode_access_token_no_scope
from app.services.user_services import UserService

router = APIRouter()


def generate_totp_secret():
    return pyotp.random_base32()


def generate_totp_uri(secret, user_email):
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email, issuer_name="YourAppName"
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserCreateResponse:
    user = await decode_access_token_no_scope(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )

    return UserCreateResponse(
        username=user.username,
        email=user.email,
        role=user.role,
    )


@router.post("/user/enable-mfa")
async def enable_mfa(
    user: UserCreateResponse = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    secret = generate_totp_secret()
    db_user = await UserService.find_by_username_or_email(db_session, user.username)
    db_user.totp_secret = secret
    db_session.add(db_user)
    await db_session.commit()
    totp_uri = generate_totp_uri(secret, user.email)

    # Return the TOTP URI
    # for QR code generation in the frontend
    return {
        "totp_uri": totp_uri,
        "secret_numbers": pyotp.TOTP(secret).now(),
    }


@router.post("/verify-totp")
async def verify_totp(
    code: str,
    username: str,
    session: AsyncSession = Depends(get_db),
):
    user = await UserService.find_by_username_or_email(session, username)
    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not activated",
        )

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP token",
        )
    # Proceed with granting access
    # or performing the sensitive operation
    return {"message": "TOTP token verified successfully"}
