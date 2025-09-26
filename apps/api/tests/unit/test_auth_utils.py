"""
Unit tests for authentication utilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from jose import jwt
import sys
from pathlib import Path

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from auth_utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    verify_token,
    get_user_by_email,
    authenticate_user
)
from models import User


class TestPasswordHashing:
    """Test password hashing and verification."""

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.hash')
    def test_hash_password(self, mock_hash):
        """Test password hashing."""
        password = "testpassword123"
        mock_hash.return_value = "$2b$12$mocked.hash.value"
        
        hashed = hash_password(password)
        
        assert hashed == "$2b$12$mocked.hash.value"
        mock_hash.assert_called_once_with(password)

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.verify')
    def test_verify_password_correct(self, mock_verify):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = "$2b$12$mocked.hash.value"
        mock_verify.return_value = True
        
        result = verify_password(password, hashed)
        
        assert result == True
        mock_verify.assert_called_once_with(password, hashed)

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.verify')
    def test_verify_password_incorrect(self, mock_verify):
        """Test password verification with incorrect password."""
        wrong_password = "wrongpassword"
        hashed = "$2b$12$mocked.hash.value"
        mock_verify.return_value = False
        
        result = verify_password(wrong_password, hashed)
        
        assert result == False
        mock_verify.assert_called_once_with(wrong_password, hashed)

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.hash')
    def test_hash_password_truncation(self, mock_hash):
        """Test that long passwords are truncated to 72 bytes."""
        long_password = "a" * 100  # 100 characters
        mock_hash.return_value = "$2b$12$mocked.hash.value"
        
        hashed = hash_password(long_password)
        
        # Should not raise an error
        assert isinstance(hashed, str)
        
        # Check that the password was truncated before hashing
        # The mock should be called with a password that's 72 bytes or less
        called_password = mock_hash.call_args[0][0]
        assert len(called_password.encode('utf-8')) <= 72


class TestJWTTokens:
    """Test JWT token creation and verification."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        
        # Decode and check expiry
        from config import get_settings
        settings = get_settings()
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        
        # Should expire in approximately 30 minutes
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_diff = exp_time - now
        
        assert 25 <= time_diff.total_seconds() / 60 <= 35  # ~30 minutes

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        
        assert payload is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        
        assert payload is None


class TestUserAuthentication:
    """Test user authentication functions."""

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(self, db_session, test_user):
        """Test getting user by email when user exists."""
        user = await get_user_by_email(db_session, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
        assert user.full_name == test_user.full_name

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_exists(self, db_session):
        """Test getting user by email when user doesn't exist."""
        user = await get_user_by_email(db_session, "nonexistent@example.com")
        
        assert user is None

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_authenticate_user_valid(self, db_session, test_user):
        """Test user authentication with valid credentials."""
        user = await authenticate_user(db_session, test_user.email, "testpassword123")
        
        assert user is not None
        assert user.email == test_user.email

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Test user authentication with wrong password."""
        user = await authenticate_user(db_session, test_user.email, "wrongpassword")
        
        assert user is False

    @pytest.mark.unit
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, db_session):
        """Test user authentication with nonexistent user."""
        user = await authenticate_user(db_session, "nonexistent@example.com", "password")
        
        assert user is False


class TestAuthErrorHandling:
    """Test error handling in authentication."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_hash_password_empty_string(self):
        """Test hashing empty password."""
        hashed = hash_password("")
        
        assert isinstance(hashed, str)
        assert verify_password("", hashed) == True

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        result = verify_password("password", "")
        
        # Should handle gracefully
        assert result == False

    @pytest.mark.unit
    @pytest.mark.auth
    def test_create_token_empty_data(self):
        """Test token creation with empty data."""
        token = create_access_token({})
        
        assert isinstance(token, str)
        
        payload = verify_token(token)
        assert payload is not None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_verify_token_malformed(self):
        """Test token verification with malformed token."""
        malformed_tokens = [
            "not.a.token",
            "too.short",
            "",
            "header.payload",  # Missing signature
            "header.payload.signature.extra"  # Too many parts
        ]
        
        for token in malformed_tokens:
            payload = verify_token(token)
            assert payload is None
