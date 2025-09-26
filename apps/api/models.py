"""
Database models for the application.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    role = Column(String, default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="owner")


class Channel(Base):
    """Marketing channel model."""
    
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # paid_search, social_media, television, etc.
    category = Column(String, nullable=False)  # digital, traditional
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaigns = relationship("Campaign", secondary="campaign_channels", back_populates="channels")
    performance_data = relationship("ChannelPerformance", back_populates="channel")


class Campaign(Base):
    """Marketing campaign model."""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    budget = Column(Float, nullable=False)
    target_audience = Column(String, nullable=True)
    status = Column(String, default="active")  # active, paused, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="campaigns")
    channels = relationship("Channel", secondary="campaign_channels", back_populates="campaigns")
    performance_data = relationship("CampaignPerformance", back_populates="campaign")


# Association table for many-to-many relationship between campaigns and channels
from sqlalchemy import Table
campaign_channels = Table(
    'campaign_channels',
    Base.metadata,
    Column('campaign_id', Integer, ForeignKey('campaigns.id'), primary_key=True),
    Column('channel_id', Integer, ForeignKey('channels.id'), primary_key=True)
)


class ChannelPerformance(Base):
    """Channel performance data for MMM analysis."""
    
    __tablename__ = "channel_performance"
    
    id = Column(Integer, primary_key=True, index=True)
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


class CampaignPerformance(Base):
    """Campaign performance data."""
    
    __tablename__ = "campaign_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    date = Column(DateTime, nullable=False)
    total_spend = Column(Float, nullable=False)
    total_conversions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    roi = Column(Float, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="performance_data")


class ResponseCurve(Base):
    """Response curve data for diminishing returns analysis."""
    
    __tablename__ = "response_curves"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    spend_level = Column(Float, nullable=False)
    predicted_conversions = Column(Float, nullable=False)
    marginal_roi = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    channel = relationship("Channel")


class MMMModelData(Base):
    """Store Google Meridian MMM model data and results."""
    
    __tablename__ = "mmm_model_data"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=True)
    data_period_start = Column(DateTime, nullable=False)
    data_period_end = Column(DateTime, nullable=False)
    model_results = Column(JSON, nullable=True)  # Store processed model results
    contribution_data = Column(JSON, nullable=True)  # Channel contribution data
    response_curves_data = Column(JSON, nullable=True)  # Response curve data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
