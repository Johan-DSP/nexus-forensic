from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from typing import Optional


# ============================================================
# USER
# ============================================================
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=200)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# AUTH
# ============================================================
class UserLogin(BaseModel):
    """Login: acepta email O username en el campo `identifier`."""
    identifier: str = Field(..., description="Email o username")
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
