from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class Role(str, Enum):
    basic = "basic"
    premium = "premium"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    username: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(
        default=Role.basic
    )
    totp_secret: Mapped[str] = mapped_column(
        nullable=True
    )

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role
    model_config = {
        "from_attributes": True  # Allows SQLAlchemy models to be converted to Pydantic models
    }


class UserCreateResponse(BaseModel):
    username: str
    email: EmailStr
    model_config = {
        "from_attributes": True  # Allows SQLAlchemy models to be converted to Pydantic models
    }


class ResponseCreateUser(BaseModel):
    message: Annotated[
        str, Field(default="user created")
    ]
    user: UserCreateResponse
    model_config = {
        "from_attributes": True  # Allows SQLAlchemy models to be converted to Pydantic models
    }