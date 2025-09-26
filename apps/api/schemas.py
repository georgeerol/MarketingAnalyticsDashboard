"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None


# Channel schemas
class ChannelBase(BaseModel):
    name: str
    type: str
    category: str
    description: Optional[str] = None


class ChannelCreate(ChannelBase):
    pass


class ChannelResponse(ChannelBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Campaign schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    budget: float
    target_audience: Optional[str] = None


class CampaignCreate(CampaignBase):
    channel_ids: List[int] = []


class CampaignResponse(CampaignBase):
    id: int
    status: str
    created_at: datetime
    owner_id: int
    channels: List[ChannelResponse] = []
    
    class Config:
        from_attributes = True


# Performance data schemas
class ChannelPerformanceResponse(BaseModel):
    id: int
    channel_id: int
    date: datetime
    spend: float
    conversions: int
    contribution_percentage: Optional[float] = None
    efficiency_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# MMM specific schemas
class ContributionData(BaseModel):
    channel_name: str
    contribution_percentage: float
    spend: float
    incremental_conversions: int
    efficiency_score: float


class ResponseCurvePoint(BaseModel):
    spend: float
    conversions: float


class ResponseCurveData(BaseModel):
    channel_name: str
    curve_points: List[ResponseCurvePoint]


class MMMDashboardData(BaseModel):
    contribution_data: List[ContributionData]
    response_curves: List[ResponseCurveData]
    total_spend: float
    total_conversions: int
    period_start: datetime
    period_end: datetime
