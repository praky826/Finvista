"""
User & Auth Schemas — Registration, login, and user profile validation.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class RegisterRequest(BaseModel):
    """10-step wizard Step 2: Authentication details."""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    username: str = Field(..., min_length=6, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    account_type: str = Field(default="personal")  # personal | business | both

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric with underscores only")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least 1 number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least 1 special character")
        return v

    @field_validator("account_type")
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        if v not in ("personal", "business", "both"):
            raise ValueError("Account type must be 'personal', 'business', or 'both'")
        return v


class LoginRequest(BaseModel):
    """Login credentials."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    success: bool = True
    user_id: int
    token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    message: str = "Login successful"


class UserResponse(BaseModel):
    """Public user profile."""
    user_id: int
    full_name: str
    email: str
    username: str
    account_type: str
    monthly_income: Optional[float] = 0
    monthly_expenses: Optional[float] = 0

    class Config:
        from_attributes = True


class UpdateIncomeRequest(BaseModel):
    """Update monthly income and expenses."""
    monthly_income: Optional[float] = Field(None, gt=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    other_monthly_income: Optional[float] = Field(None, ge=0)
