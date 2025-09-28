"""
Integration tests for authentication API endpoints.

This module contains tests for all authentication-related endpoints
including login, registration, user info retrieval, and complete authentication workflows.
"""

import pytest
from httpx import AsyncClient
from datetime import timedelta
from app.core.security import create_access_token

# Test constants
TEST_PASSWORD = "testpassword123"
WEAK_PASSWORD = "123"
INVALID_EMAIL = "invalid-email"


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        """Test login with valid credentials using OAuth2 form data format."""
        login_data = {
            "email": test_user.email,
            "password": TEST_PASSWORD
        }
        
        response = await client.post(
            "/api/v1/auth/login", 
            data={"username": login_data["email"], "password": login_data["password"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_form_data(self, client: AsyncClient, test_user):
        """Test login with direct form data (OAuth2 standard format)."""
        login_data = {
            "username": test_user.email,
            "password": TEST_PASSWORD
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email address."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": TEST_PASSWORD
        }
        
        response = await client.post(
            "/api/v1/auth/login", 
            data={"username": login_data["email"], "password": login_data["password"]}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Test login with incorrect password for existing user."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post(
            "/api/v1/auth/login", 
            data={"username": login_data["email"], "password": login_data["password"]}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)


    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration with valid data and automatic login."""
        register_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
            "company": "New Company"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify token response
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        
        # Verify user data
        assert "user" in data
        user_data = data["user"]
        assert user_data["email"] == "newuser@example.com"
        assert user_data["full_name"] == "New User"
        assert user_data["company"] == "New Company"
        assert user_data["role"] == "user"
        assert user_data["is_active"] is True
        assert "id" in user_data
        assert "created_at" in user_data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email."""
        register_data = {
            "email": test_user.email,  # Existing email
            "password": "newpassword123",
            "full_name": "Another User"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with malformed email address."""
        register_data = {
            "email": INVALID_EMAIL,
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with password that doesn't meet security requirements."""
        register_data = {
            "email": "newuser@example.com",
            "password": WEAK_PASSWORD,  # Too short
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_authenticated(self, client: AsyncClient, auth_headers):
        """Test getting current user info when authenticated."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "email" in data
        assert "full_name" in data
        assert "company" in data
        assert "role" in data
        assert "is_active" in data
        assert "created_at" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, client: AsyncClient):
        """Test getting current user info when not authenticated."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, client: AsyncClient, test_user):
        """Test getting current user info with expired JWT token."""
        # Create an expired token (negative expiration time)
        expired_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)


class TestAuthWorkflow:
    """Test complete authentication workflows and user journeys."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_login_workflow(self, client: AsyncClient):
        """
        Test complete user journey: register -> get user info -> login -> get user info.
        
        This test validates the entire authentication flow from user registration
        through subsequent logins, ensuring tokens work correctly and user data
        remains consistent across authentication events.
        """
        # Step 1: Register new user
        register_data = {
            "email": "workflow@example.com",
            "password": "workflowpass123",
            "full_name": "Workflow User",
            "company": "Workflow Company"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        register_result = register_response.json()
        first_token = register_result["access_token"]
        
        # Step 2: Use token to get user info
        headers = {"Authorization": f"Bearer {first_token}"}
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_info = me_response.json()
        assert user_info["email"] == "workflow@example.com"
        
        # Step 3: Login with same credentials
        login_data = {
            "email": "workflow@example.com",
            "password": "workflowpass123"
        }
        
        login_response = await client.post("/api/v1/auth/login", data={"username": login_data["email"], "password": login_data["password"]})
        assert login_response.status_code == 200
        
        login_result = login_response.json()
        second_token = login_result["access_token"]
        
        # Step 4: Use new token to get user info
        headers = {"Authorization": f"Bearer {second_token}"}
        me_response2 = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response2.status_code == 200
        
        user_info2 = me_response2.json()
        assert user_info2["email"] == "workflow@example.com"
        assert user_info2["id"] == user_info["id"]  # Same user

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_empty_credentials(self, client: AsyncClient):
        """Test login with empty username and password."""
        response = await client.post("/api/v1/auth/login", data={})
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        register_data = {
            "email": "incomplete@example.com"
            # Missing password and full_name
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_malformed_token(self, client: AsyncClient):
        """Test getting current user info with malformed Authorization header."""
        # Test various malformed headers
        malformed_headers = [
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "InvalidScheme token"},  # Wrong scheme
            {"Authorization": "Bearer "},  # Empty token
            {"Authorization": "token"},  # Missing Bearer
        ]
        
        for headers in malformed_headers:
            response = await client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data