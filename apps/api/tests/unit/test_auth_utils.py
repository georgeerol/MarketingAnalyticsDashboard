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
    @patch('auth_utils.jwt.encode')
    def test_create_access_token_with_expiry(self, mock_jwt_encode):
        """Test JWT token creation with custom expiry."""
        mock_jwt_encode.return_value = "mocked.jwt.token"
        
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert token == "mocked.jwt.token"
        
        # Verify jwt.encode was called with correct parameters
        mock_jwt_encode.assert_called_once()
        call_args = mock_jwt_encode.call_args[0]
        
        # Check that the payload contains the expected data
        payload = call_args[0]
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.jwt.decode')
    def test_verify_token_valid(self, mock_jwt_decode):
        """Test token verification with valid token."""
        mock_jwt_decode.return_value = {"sub": "test@example.com", "exp": 1234567890}
        
        token = "valid.jwt.token"
        username = verify_token(token)
        
        assert username is not None
        assert isinstance(username, str)
        assert username == "test@example.com"
        
        # Verify jwt.decode was called
        mock_jwt_decode.assert_called_once()

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


class TestAuthErrorHandling:
    """Test error handling in authentication."""

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.hash')
    def test_hash_password_empty_string(self, mock_hash):
        """Test hashing empty password."""
        mock_hash.return_value = "$2b$12$empty.hash.value"
        
        hashed = hash_password("")
        
        assert hashed == "$2b$12$empty.hash.value"
        mock_hash.assert_called_once_with("")

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.pwd_context.verify')
    def test_verify_password_empty_hash(self, mock_verify):
        """Test password verification with empty hash."""
        mock_verify.return_value = False
        
        result = verify_password("password", "")
        
        # Should handle gracefully
        assert result == False
        mock_verify.assert_called_once_with("password", "")

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


class TestDatabaseOperations:
    """Test database operations with mocking."""

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.Session')
    def test_get_user_by_email_found(self, mock_session_class):
        """Test getting user by email when user exists."""
        # Mock the session and query
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.id = 1
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_session.query.return_value = mock_query
        
        # Test the function
        result = get_user_by_email(mock_session, "test@example.com")
        
        assert result == mock_user
        assert result.email == "test@example.com"

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.Session')
    def test_get_user_by_email_not_found(self, mock_session_class):
        """Test getting user by email when user doesn't exist."""
        # Mock the session and query
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Test the function
        result = get_user_by_email(mock_session, "nonexistent@example.com")
        
        assert result is None

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.get_user_by_email')
    @patch('auth_utils.verify_password')
    def test_authenticate_user_valid(self, mock_verify_password, mock_get_user):
        """Test user authentication with valid credentials."""
        # Mock user and password verification
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        mock_get_user.return_value = mock_user
        mock_verify_password.return_value = True
        
        # Test authentication
        mock_session = Mock()
        result = authenticate_user(mock_session, "test@example.com", "correct_password")
        
        assert result == mock_user
        mock_get_user.assert_called_once_with(mock_session, "test@example.com")
        mock_verify_password.assert_called_once_with("correct_password", "hashed_password")

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.get_user_by_email')
    @patch('auth_utils.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify_password, mock_get_user):
        """Test user authentication with wrong password."""
        # Mock user and password verification
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        mock_get_user.return_value = mock_user
        mock_verify_password.return_value = False
        
        # Test authentication
        mock_session = Mock()
        result = authenticate_user(mock_session, "test@example.com", "wrong_password")
        
        assert result is None
        mock_verify_password.assert_called_once_with("wrong_password", "hashed_password")

    @pytest.mark.unit
    @pytest.mark.auth
    @patch('auth_utils.get_user_by_email')
    def test_authenticate_user_nonexistent(self, mock_get_user):
        """Test user authentication with nonexistent user."""
        # Mock user not found
        mock_get_user.return_value = None
        
        # Test authentication
        mock_session = Mock()
        result = authenticate_user(mock_session, "nonexistent@example.com", "any_password")
        
        assert result is None
        mock_get_user.assert_called_once_with(mock_session, "nonexistent@example.com")
