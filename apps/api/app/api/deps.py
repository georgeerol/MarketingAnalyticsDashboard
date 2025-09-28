"""
Common API dependencies.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_user
from app.models.user import User
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.mmm_service import MMMService
from app.services.interfaces import (
    UserServiceProtocol,
    AuthServiceProtocol,
    MMMServiceProtocol,
)


def get_user_service(db: Session = Depends(get_db)) -> UserServiceProtocol:
    """Get user service instance."""
    return UserService(db)


def get_auth_service(
    user_service: UserServiceProtocol = Depends(get_user_service)
) -> AuthServiceProtocol:
    """Get authentication service instance."""
    return AuthService(user_service)


def get_mmm_service() -> MMMServiceProtocol:
    """Get MMM service instance."""
    return MMMService()


def get_current_user_dep(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current authenticated user."""
    return current_user


def get_current_active_user_dep(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get current active user."""
    return current_user


