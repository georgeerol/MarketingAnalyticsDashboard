"""
Base model class and common mixins.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        nullable=True
    )


class BaseModel(Base):
    """Abstract base model with common fields."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
