"""
Campaign and Channel models for marketing campaign management.
"""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Text, 
    ForeignKey, Integer, Table
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin, Base


# Association table for many-to-many relationship between campaigns and channels
campaign_channels = Table(
    'campaign_channels',
    Base.metadata,
    Column('campaign_id', Integer, ForeignKey('campaigns.id'), primary_key=True),
    Column('channel_id', Integer, ForeignKey('channels.id'), primary_key=True)
)


class Channel(BaseModel, TimestampMixin):
    """Marketing channel model."""
    
    __tablename__ = "channels"
    
    # Channel fields
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # paid_search, social_media, television, etc.
    category = Column(String, nullable=False)  # digital, traditional
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    campaigns = relationship(
        "Campaign", 
        secondary=campaign_channels, 
        back_populates="channels"
    )
    performance_data = relationship("ChannelPerformance", back_populates="channel")
    response_curves = relationship("ResponseCurve", back_populates="channel")
    
    def __repr__(self) -> str:
        """String representation of the channel."""
        return f"<Channel(id={self.id}, name='{self.name}', type='{self.type}')>"


class Campaign(BaseModel, TimestampMixin):
    """Marketing campaign model."""
    
    __tablename__ = "campaigns"
    
    # Campaign fields
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    budget = Column(Float, nullable=False)
    target_audience = Column(String, nullable=True)
    status = Column(String, default="active")  # active, paused, completed
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="campaigns")
    channels = relationship(
        "Channel", 
        secondary=campaign_channels, 
        back_populates="campaigns"
    )
    performance_data = relationship("CampaignPerformance", back_populates="campaign")
    
    def __repr__(self) -> str:
        """String representation of the campaign."""
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if campaign is active."""
        return self.status == "active"


class ChannelPerformance(BaseModel):
    """Channel performance data for MMM analysis."""
    
    __tablename__ = "channel_performance"
    
    # Performance fields
    channel_id = Column(Integer, ForeignKey("channels.id"))
    date = Column(DateTime, nullable=False)
    spend = Column(Float, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    contribution_percentage = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    incremental_conversions = Column(Integer, nullable=True)
    
    # Relationships
    channel = relationship("Channel", back_populates="performance_data")
    
    def __repr__(self) -> str:
        """String representation of channel performance."""
        return f"<ChannelPerformance(id={self.id}, channel_id={self.channel_id}, date={self.date})>"


class CampaignPerformance(BaseModel):
    """Campaign performance data."""
    
    __tablename__ = "campaign_performance"
    
    # Performance fields
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    date = Column(DateTime, nullable=False)
    total_spend = Column(Float, nullable=False)
    total_conversions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    roi = Column(Float, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="performance_data")
    
    def __repr__(self) -> str:
        """String representation of campaign performance."""
        return f"<CampaignPerformance(id={self.id}, campaign_id={self.campaign_id}, date={self.date})>"
