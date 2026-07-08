from datetime import datetime
import enum

from pydantic import BaseModel, EmailStr


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    ANALYST = "ANALYST"


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.USER
    avatar: str | None = None
    organization: str | None = None
    country: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    avatar: str | None = None
    organization: str | None = None
    country: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse