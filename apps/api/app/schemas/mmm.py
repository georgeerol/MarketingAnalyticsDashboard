"""
MMM (Media Mix Modeling) related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel, Field


class ResponseCurvePoint(BaseModel):
    """Schema for a single point on a response curve."""
    
    spend: float = Field(..., ge=0, description="Spend amount")
    response: float = Field(..., ge=0, description="Response/conversions")




class MMMModelInfo(BaseModel):
    """Schema for MMM model information."""
    
    model_type: str = Field(..., description="Type of MMM model")
    version: str = Field(..., description="Model version")
    training_period: str = Field(..., description="Training period")
    channels: list[str] = Field(..., description="List of channels")
    data_frequency: str = Field(..., description="Data frequency")
    total_weeks: int = Field(..., description="Total number of weeks")
    data_source: str = Field(..., description="Data source")




class MMMChannelSummary(BaseModel):
    """Schema for MMM channel summary."""
    
    name: str = Field(..., description="Channel name")
    total_spend: float = Field(..., ge=0, description="Total spend")
    total_contribution: float = Field(..., ge=0, description="Total contribution")
    contribution_share: float = Field(..., ge=0, le=1, description="Contribution share")
    efficiency: float = Field(..., ge=0, description="Efficiency score")
    avg_weekly_spend: float = Field(..., ge=0, description="Average weekly spend")
    avg_weekly_contribution: float = Field(..., ge=0, description="Average weekly contribution")


