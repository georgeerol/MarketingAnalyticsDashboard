"""
Service protocols for dependency injection.

Defines interfaces that services implement for easier testing.
"""

from typing import Protocol, Optional, List, Dict, Any, runtime_checkable
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import UserLogin, AuthResponse
from app.schemas.mmm import MMMModelInfo, MMMChannelSummary


@runtime_checkable
class UserServiceProtocol(Protocol):
    """Protocol for user management operations."""
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        ...
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        ...


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Protocol for authentication operations."""
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        ...
    
    def login(self, login_data: UserLogin) -> AuthResponse:
        """Perform user login and generate access token."""
        ...
    
    def get_current_user_from_token(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        ...
    


@runtime_checkable
class MMMServiceProtocol(Protocol):
    """Protocol for MMM model operations."""
    
    def get_model_info(self) -> MMMModelInfo:
        """Get detailed information about the MMM model."""
        ...
    
    def get_channel_names(self) -> List[str]:
        """Get list of media channel names from the model."""
        ...
    
    def get_contribution_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get contribution data for channels from the loaded MMM model."""
        ...
    
    def get_response_curves(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get response curves for channels from the loaded MMM model."""
        ...
    
    def get_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """Get summary statistics for all channels."""
        ...
