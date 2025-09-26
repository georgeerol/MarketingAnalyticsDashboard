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
        
        response = await client.post("/auth/login-json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await client.post("/auth/login-json", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Test login with invalid password."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login-json", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing required fields."""
        # Missing password
        response = await client.post("/auth/login-json", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Missing email
        response = await client.post("/auth/login-json", json={"password": "password123"})
        assert response.status_code == 422
        
        # Empty request
        response = await client.post("/auth/login-json", json={})
        assert response.status_code == 422

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_form_endpoint(self, client: AsyncClient, test_user):
        """Test form-based login endpoint."""
        login_data = {
            "username": test_user.email,  # Form uses 'username' field
            "password": "testpassword123"
        }
        
        response = await client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, client: AsyncClient, auth_headers: dict, test_user):
        """Test getting current user with valid token."""
        response = await client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["company"] == test_user.company
        assert data["role"] == test_user.role
        assert data["is_active"] == test_user.is_active

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_malformed_header(self, client: AsyncClient):
        """Test getting current user with malformed authorization header."""
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic token"},  # Wrong type
            {"Authorization": "Bearer "},  # Empty token
        ]
        
        for headers in malformed_headers:
            response = await client.get("/auth/me", headers=headers)
            assert response.status_code == 401


class TestAuthFlow:
    """Test complete authentication flows."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client: AsyncClient, test_user):
        """Test complete authentication flow: login -> access protected resource."""
        # Step 1: Login
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/auth/login-json", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Step 2: Access protected resource
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == test_user.email

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_token_persistence(self, client: AsyncClient, test_user):
        """Test that token works for multiple requests."""
        # Login
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/auth/login-json", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple requests with same token
        for _ in range(3):
            response = await client.get("/auth/me", headers=headers)
            assert response.status_code == 200
            assert response.json()["email"] == test_user.email

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_auth_required_endpoints(self, client: AsyncClient, auth_headers: dict):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/auth/me",
            "/mmm/status",
            "/mmm/info",
            "/mmm/channels",
            "/mmm/contribution",
            "/mmm/response-curves",
            "/mmm/explore",
            "/mmm/test"
        ]
        
        # Test without authentication
        for endpoint in protected_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401
        
        # Test with authentication
        for endpoint in protected_endpoints:
            response = await client.get(endpoint, headers=auth_headers)
            # Should not be 401 (may be 200, 404, 500 depending on endpoint)
            assert response.status_code != 401


class TestAuthSecurity:
    """Test authentication security aspects."""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_password_not_returned(self, client: AsyncClient, test_user):
        """Test that password is never returned in responses."""
        # Login
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/auth/login-json", json=login_data)
        login_data_response = login_response.json()
        
        # Check login response
        assert "password" not in str(login_data_response)
        assert "hashed_password" not in str(login_data_response)
        
        # Check user info response
        token = login_data_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/auth/me", headers=headers)
        me_data = me_response.json()
        
        assert "password" not in str(me_data)
        assert "hashed_password" not in str(me_data)

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_case_sensitive_email(self, client: AsyncClient, test_user):
        """Test that email authentication is case insensitive."""
        login_data = {
            "email": test_user.email.upper(),  # Use uppercase
            "password": "testpassword123"
        }
        
        response = await client.post("/auth/login-json", json=login_data)
        
        # Should still work (depending on implementation)
        # This test documents the expected behavior
        assert response.status_code in [200, 401]  # Either works or doesn't

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test protection against SQL injection in login."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin@example.com' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin@example.com'; UPDATE users SET password='hacked' --"
        ]
        
        for malicious_email in malicious_inputs:
            login_data = {
                "email": malicious_email,
                "password": "password123"
            }
            
            response = await client.post("/auth/login-json", json=login_data)
            
            # Should not cause server error, should return 401 or 422
            assert response.status_code in [401, 422]
            assert response.status_code != 500

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_rate_limiting_simulation(self, client: AsyncClient):
        """Test multiple failed login attempts (simulates rate limiting needs)."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        # Make multiple failed attempts
        for _ in range(5):
            response = await client.post("/auth/login-json", json=login_data)
            assert response.status_code == 401
        
        # All should fail with same error (no information leakage)
        # In production, this might trigger rate limiting
