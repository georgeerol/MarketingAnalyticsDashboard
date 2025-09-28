"""
User-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    company: Optional[str] = Field(None, max_length=100, description="User's company")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=100, description="User's password")


class UserResponse(UserBase):
    """Schema for user response data."""
    
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
