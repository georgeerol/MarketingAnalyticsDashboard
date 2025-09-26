"""
MMM (Media Mix Modeling) related models.
"""

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class MMMModelData(BaseModel, TimestampMixin):
    """Store Google Meridian MMM model data and results."""
    
    __tablename__ = "mmm_model_data"
    
    # Model metadata
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=True)
    data_period_start = Column(DateTime, nullable=False)
    data_period_end = Column(DateTime, nullable=False)
    
    # Model results (stored as JSON)
    model_results = Column(JSON, nullable=True)  # Store processed model results
    contribution_data = Column(JSON, nullable=True)  # Channel contribution data
    response_curves_data = Column(JSON, nullable=True)  # Response curve data
    
    def __repr__(self) -> str:
        """String representation of MMM model data."""
        return f"<MMMModelData(id={self.id}, model_name='{self.model_name}', version='{self.model_version}')>"


class ResponseCurve(BaseModel, TimestampMixin):
    """Response curve data for diminishing returns analysis."""
    
    __tablename__ = "response_curves"
    
    # Curve data
    channel_id = Column(Integer, ForeignKey("channels.id"))
    spend_level = Column(Float, nullable=False)
    predicted_conversions = Column(Float, nullable=False)
    marginal_roi = Column(Float, nullable=True)
    
    # Relationships
    channel = relationship("Channel", back_populates="response_curves")
    
    def __repr__(self) -> str:
        """String representation of response curve."""
        return f"<ResponseCurve(id={self.id}, channel_id={self.channel_id}, spend_level={self.spend_level})>"
