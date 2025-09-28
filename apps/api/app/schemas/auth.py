"""
Authentication-related Pydantic schemas.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for token payload data."""
    
    username: Optional[str] = Field(None, description="Username from token")


class AuthResponse(BaseModel):
    """Schema for authentication response with user data."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
