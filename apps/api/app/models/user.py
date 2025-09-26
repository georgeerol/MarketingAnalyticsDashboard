"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # User fields
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    role = Column(String, default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="owner")
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"
