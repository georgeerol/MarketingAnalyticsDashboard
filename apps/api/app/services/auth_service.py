"""
Handles user authentication and JWT tokens.
"""

from datetime import timedelta
from typing import Optional

from app.models.user import User
from app.schemas.auth import UserLogin, AuthResponse
from app.schemas.user import UserResponse
from app.core.security import verify_password, create_access_token
from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.interfaces import UserServiceProtocol

settings = get_settings()
logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""
    pass


class AuthService:
    """Handles login, logout, and token generation."""
    
    def __init__(self, user_service: UserServiceProtocol):
        self.user_service = user_service
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Check if email/password combo is valid.
        
        Returns User if valid, None if not.
        """
        user = self.user_service.get_user_by_email(email)
        
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user {email} is inactive")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for email {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    def login(self, login_data: UserLogin) -> AuthResponse:
        """
        Log in user and return JWT token.
        
        Raises AuthenticationError if login fails.
        """
        user = self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        # Create user response
        user_response = UserResponse.model_validate(user)
        
        logger.info(f"Generated access token for user: {user.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    def get_current_user_from_token(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            User instance if token is valid, None otherwise
        """
        from app.core.security import verify_token
        
        username = verify_token(token)
        if not username:
            return None
        
        user = self.user_service.get_user_by_email(username)
        if not user or not user.is_active:
            return None
        
        return user
    
