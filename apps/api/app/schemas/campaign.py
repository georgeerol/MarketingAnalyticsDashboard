"""
Campaign and Channel related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Base channel schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Channel name")
    type: str = Field(..., description="Channel type (e.g., paid_search, social_media)")
    category: str = Field(..., description="Channel category (e.g., digital, traditional)")
    description: Optional[str] = Field(None, max_length=500, description="Channel description")


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel."""
    pass


class ChannelUpdate(BaseModel):
    """Schema for updating channel information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ChannelResponse(ChannelBase):
    """Schema for channel response data."""
    
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CampaignBase(BaseModel):
    """Base campaign schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(None, max_length=1000, description="Campaign description")
    start_date: datetime = Field(..., description="Campaign start date")
    end_date: datetime = Field(..., description="Campaign end date")
    budget: float = Field(..., gt=0, description="Campaign budget")
    target_audience: Optional[str] = Field(None, max_length=200, description="Target audience")


class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign."""
    
    channel_ids: list[int] = Field(default=[], description="List of channel IDs")


class CampaignUpdate(BaseModel):
    """Schema for updating campaign information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, gt=0)
    target_audience: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = None
    channel_ids: Optional[list[int]] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response data."""
    
    id: int
    status: str
    created_at: datetime
    owner_id: int
    channels: list[ChannelResponse] = []
    
    model_config = {"from_attributes": True}


class ChannelPerformanceResponse(BaseModel):
    """Schema for channel performance data."""
    
    id: int
    channel_id: int
    date: datetime
    spend: float
    impressions: int
    clicks: int
    conversions: int
    contribution_percentage: Optional[float] = None
    efficiency_score: Optional[float] = None
    incremental_conversions: Optional[int] = None
    
    model_config = {"from_attributes": True}


class CampaignPerformanceResponse(BaseModel):
    """Schema for campaign performance data."""
    
    id: int
    campaign_id: int
    date: datetime
    total_spend: float
    total_conversions: int
    total_revenue: float
    roi: Optional[float] = None
    
    model_config = {"from_attributes": True}
