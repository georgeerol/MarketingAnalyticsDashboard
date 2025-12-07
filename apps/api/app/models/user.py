"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # User fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)
    role = Column(String(20), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"
