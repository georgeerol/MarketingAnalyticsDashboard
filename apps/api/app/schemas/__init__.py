"""
Pydantic schemas package for API request/response models.
"""

from app.schemas.user import (
    UserBase, UserCreate, UserResponse, UserUpdate
)
from app.schemas.auth import (
    Token, TokenData, AuthResponse, UserLogin
)
from app.schemas.campaign import (
    ChannelBase, ChannelCreate, ChannelResponse, ChannelUpdate,
    CampaignBase, CampaignCreate, CampaignResponse, CampaignUpdate,
    ChannelPerformanceResponse, CampaignPerformanceResponse
)
from app.schemas.mmm import (
    ContributionData, ResponseCurvePoint, ResponseCurveData,
    MMMDashboardData, MMMModelInfo, MMMStatus
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserResponse", "UserUpdate",
    # Auth schemas  
    "Token", "TokenData", "AuthResponse", "UserLogin",
    # Campaign schemas
    "ChannelBase", "ChannelCreate", "ChannelResponse", "ChannelUpdate",
    "CampaignBase", "CampaignCreate", "CampaignResponse", "CampaignUpdate",
    "ChannelPerformanceResponse", "CampaignPerformanceResponse",
    # MMM schemas
    "ContributionData", "ResponseCurvePoint", "ResponseCurveData",
    "MMMDashboardData", "MMMModelInfo", "MMMStatus",
]
