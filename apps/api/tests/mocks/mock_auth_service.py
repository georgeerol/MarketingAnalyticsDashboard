"""
Mock implementation of AuthServiceProtocol for testing.

This demonstrates how protocols make authentication testing simple and predictable.
"""

from typing import Optional
from app.services.interfaces import AuthServiceProtocol, UserServiceProtocol
from app.schemas.auth import UserLogin, AuthResponse
from app.schemas.user import UserResponse
from tests.mocks.mock_user_service import MockUser


class MockAuthService(AuthServiceProtocol):
    """
    Mock implementation of AuthServiceProtocol.
    
    Provides predictable authentication behavior for testing without real JWT tokens.
    """
    
    def __init__(self, user_service: UserServiceProtocol):
        self.user_service = user_service
        self.valid_passwords = {
            "admin@test.com": "admin_password",
            "user@test.com": "user_password",
            "test_password": "test_password",  # Generic test password
        }
        self.generated_tokens = []  # Track generated tokens for testing
    
    def authenticate_user(self, email: str, password: str) -> Optional[MockUser]:
        """
        Authenticate a user with email and password.
        
        Uses predictable password checking for testing.
        """
        user = self.user_service.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        # Check password (simplified for testing)
        valid_password = self.valid_passwords.get(email, "test_password")
        if password != valid_password:
            return None
        
        return user
    
    def login(self, login_data: UserLogin) -> AuthResponse:
        """
        Perform user login and generate access token.
        
        Returns predictable tokens for testing.
        """
        user = self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            from app.services.auth_service import AuthenticationError
            raise AuthenticationError("Invalid email or password")
        
        # Generate mock token
        mock_token = f"mock_token_{user.id}_{len(self.generated_tokens)}"
        self.generated_tokens.append(mock_token)
        
        # Create user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return AuthResponse(
            access_token=mock_token,
            token_type="bearer",
            user=user_response
        )
    
    def get_current_user_from_token(self, token: str) -> Optional[MockUser]:
        """
        Get current user from JWT token.
        
        Uses simple token parsing for testing.
        """
        if not token.startswith("mock_token_"):
            return None
        
        try:
            # Extract user ID from mock token
            parts = token.split("_")
            if len(parts) >= 3:
                user_id = int(parts[2])
                user = self.user_service.get_user_by_id(user_id)
                if user and user.is_active:
                    return user
        except (ValueError, IndexError):
            pass
        
        return None
    
    def refresh_token(self, user: MockUser) -> str:
        """
        Generate a new access token for a user.
        
        Returns predictable refresh tokens for testing.
        """
        refresh_token = f"refresh_token_{user.id}_{len(self.generated_tokens)}"
        self.generated_tokens.append(refresh_token)
        return refresh_token
    
    # Utility methods for testing
    def set_valid_password(self, email: str, password: str):
        """Set a valid password for testing."""
        self.valid_passwords[email] = password
    
    def clear_tokens(self):
        """Clear generated tokens (useful for test cleanup)."""
        self.generated_tokens.clear()
    
    def get_generated_tokens(self) -> list:
        """Get list of generated tokens for testing verification."""
        return self.generated_tokens.copy()
    
    def create_mock_token_for_user(self, user: MockUser) -> str:
        """Create a mock token for a specific user (testing utility)."""
        mock_token = f"mock_token_{user.id}_{len(self.generated_tokens)}"
        self.generated_tokens.append(mock_token)
        return mock_token
