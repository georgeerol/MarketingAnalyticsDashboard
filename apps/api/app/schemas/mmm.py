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


class ResponseCurveData(BaseModel):
    """Schema for response curve data for a channel."""
    
    channel: str = Field(..., description="Channel name")
    curves: dict[str, Any] = Field(..., description="Response curve data")


class ContributionData(BaseModel):
    """Schema for channel contribution data."""
    
    channel: str = Field(..., description="Channel name")
    data: list[float] = Field(..., description="Contribution data points")
    summary: dict[str, float] = Field(..., description="Summary statistics")


class MMMStatus(BaseModel):
    """Schema for MMM model status."""
    
    status: str = Field(..., description="Status of the MMM model")
    message: str = Field(..., description="Status message")
    file_exists: bool = Field(..., description="Whether model file exists")
    model_info: Optional[dict[str, Any]] = Field(None, description="Model information")


class MMMModelInfo(BaseModel):
    """Schema for MMM model information."""
    
    model_type: str = Field(..., description="Type of MMM model")
    version: str = Field(..., description="Model version")
    training_period: str = Field(..., description="Training period")
    channels: list[str] = Field(..., description="List of channels")
    data_frequency: str = Field(..., description="Data frequency")
    total_weeks: int = Field(..., description="Total number of weeks")
    data_source: str = Field(..., description="Data source")


class MMMDashboardData(BaseModel):
    """Schema for MMM dashboard data."""
    
    contribution_data: list[ContributionData] = Field(..., description="Channel contribution data")
    response_curves: list[ResponseCurveData] = Field(..., description="Response curves data")
    total_spend: float = Field(..., ge=0, description="Total spend")
    total_conversions: int = Field(..., ge=0, description="Total conversions")
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")


class MMMChannelSummary(BaseModel):
    """Schema for MMM channel summary."""
    
    name: str = Field(..., description="Channel name")
    total_spend: float = Field(..., ge=0, description="Total spend")
    total_contribution: float = Field(..., ge=0, description="Total contribution")
    contribution_share: float = Field(..., ge=0, le=1, description="Contribution share")
    efficiency: float = Field(..., ge=0, description="Efficiency score")
    avg_weekly_spend: float = Field(..., ge=0, description="Average weekly spend")
    avg_weekly_contribution: float = Field(..., ge=0, description="Average weekly contribution")


class MMMInsight(BaseModel):
    """Schema for MMM insights and recommendations."""
    
    type: str = Field(..., description="Insight type (success, warning, info)")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    action: Optional[str] = Field(None, description="Recommended action")
    channel: Optional[str] = Field(None, description="Related channel")
    impact: Optional[str] = Field(None, description="Expected impact level")


class MMMExportRequest(BaseModel):
    """Schema for MMM export request."""
    
    format: str = Field("json", description="Export format (json, csv, txt)")
    include_raw_data: bool = Field(False, description="Include raw model data")


class MMMExportResponse(BaseModel):
    """Schema for MMM export response."""
    
    success: bool = Field(..., description="Export success status")
    message: str = Field(..., description="Export status message")
    download_url: Optional[str] = Field(None, description="Download URL if applicable")
    data: Optional[Dict[str, Any]] = Field(None, description="Export data if inline")
