"""
Service interface protocols for dependency injection and testing.

These protocols define the contracts our services implement,
enabling easy testing and future flexibility without overengineering.
"""

from typing import Protocol, Optional, List, Dict, Any, runtime_checkable
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import UserLogin, AuthResponse
from app.schemas.mmm import MMMStatus, MMMModelInfo, MMMChannelSummary


@runtime_checkable
class UserServiceProtocol(Protocol):
    """Protocol for user management operations."""
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        ...
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[User]:
        """Get list of users with pagination."""
        ...
    
    def get_users_count(self, active_only: bool = True) -> int:
        """Get total count of users."""
        ...
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        ...
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        ...
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        ...
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
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
    
    def refresh_token(self, user: User) -> str:
        """Generate a new access token for the user."""
        ...


@runtime_checkable
class MMMServiceProtocol(Protocol):
    """Protocol for MMM model operations."""
    
    def get_model_status(self) -> MMMStatus:
        """Get the status of the MMM model."""
        ...
    
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
