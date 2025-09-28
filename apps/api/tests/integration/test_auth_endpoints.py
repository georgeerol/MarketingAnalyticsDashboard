"""
Integration tests for authentication API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        """Test login with valid credentials."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data={"username": login_data["email"], "password": login_data["password"]})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_form_data(self, client: AsyncClient, test_user):
        """Test login with form data (OAuth2 style)."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data={"username": login_data["email"], "password": login_data["password"]})
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Test login with invalid password."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", data={"username": login_data["email"], "password": login_data["password"]})
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration with valid data."""
        register_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
            "company": "New Company"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"
        assert data["user"]["company"] == "New Company"
        assert data["user"]["role"] == "user"
        assert data["user"]["is_active"] is True

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
        """Test registration with invalid email format."""
        register_data = {
            "email": "invalid-email",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        register_data = {
            "email": "newuser@example.com",
            "password": "123",  # Too short
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Validation error

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
        """Test getting current user info with expired token."""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestAuthWorkflow:
    """Test complete authentication workflows."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_register_login_workflow(self, client: AsyncClient):
        """Test complete register -> login workflow."""
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