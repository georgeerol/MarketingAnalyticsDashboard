"""
Common API dependencies.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
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


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> dict:
    """Get pagination parameters with validation."""
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 1000:
        limit = 100
    
    return {"skip": skip, "limit": limit}
