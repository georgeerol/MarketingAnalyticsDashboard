"""
Database models package.
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.base import Base
from app.models.user import User

__all__ = [
    "Base",
    "User",
]
