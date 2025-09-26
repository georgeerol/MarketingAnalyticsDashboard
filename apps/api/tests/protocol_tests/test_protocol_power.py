"""
Comprehensive tests demonstrating the power of protocol-based architecture.

These tests showcase how dependency inversion makes testing easier, more reliable,
and more maintainable.
"""

import pytest
from fastapi.testclient import TestClient

from app.services.interfaces import UserServiceProtocol, AuthServiceProtocol, MMMServiceProtocol
from tests.mocks import MockUserService, MockAuthService, MockMMMService


class TestProtocolBasedTesting:
    """
    Test suite demonstrating the benefits of protocol-based testing.
    """
    
    def test_easy_service_mocking(self, mock_user_service: UserServiceProtocol):
        """
        Test how easy it is to mock services with protocols.
        
        This test shows that we can use any implementation of UserServiceProtocol
        without changing our test code.
        """
        # Test basic functionality
        users = mock_user_service.get_users()
        assert len(users) >= 2  # Should have default test users
        
        # Test user creation
        from app.schemas.user import UserCreate
        user_data = UserCreate(
            email="protocol_test@example.com",
            password="test_password",
            full_name="Protocol Test User"
        )
        
        new_user = mock_user_service.create_user(user_data)
        assert new_user.email == "protocol_test@example.com"
        assert new_user.full_name == "Protocol Test User"
        
        # Verify user was added
        found_user = mock_user_service.get_user_by_email("protocol_test@example.com")
        assert found_user is not None
        assert found_user.id == new_user.id
    
    def test_service_composition_with_protocols(
        self, 
        mock_user_service: UserServiceProtocol, 
        mock_auth_service: AuthServiceProtocol
    ):
        """
        Test how protocols enable clean service composition.
        
        AuthService depends on UserServiceProtocol, not a concrete class.
        This makes testing much more flexible.
        """
        # Test authentication with mock services
        user = mock_auth_service.authenticate_user("admin@test.com", "admin_password")
        assert user is not None
        assert user.email == "admin@test.com"
        assert user.is_admin is True
        
        # Test failed authentication
        user = mock_auth_service.authenticate_user("admin@test.com", "wrong_password")
        assert user is None
        
        # Test login flow
        from app.schemas.auth import UserLogin
        login_data = UserLogin(email="user@test.com", password="user_password")
        
        auth_response = mock_auth_service.login(login_data)
        assert auth_response.access_token.startswith("mock_token_")
        assert auth_response.token_type == "bearer"
        assert auth_response.user.email == "user@test.com"
    
    def test_complete_api_with_mocks(self, client_with_mocks: TestClient):
        """
        Test the complete API using only mock implementations.
        
        This demonstrates the ultimate power of dependency inversion - we can
        test the entire API without any real databases or external services!
        """
        # Test registration
        user_data = {
            "email": "api_test@example.com",
            "password": "test_password",
            "full_name": "API Test User"
        }
        
        response = client_with_mocks.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["email"] == "api_test@example.com"
        assert created_user["full_name"] == "API Test User"
        
        # Test login
        login_data = {
            "username": "api_test@example.com",
            "password": "test_password"
        }
        
        response = client_with_mocks.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Test authenticated endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client_with_mocks.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_info = response.json()
        assert user_info["email"] == "api_test@example.com"
    
    def test_mmm_service_mocking(self, mock_mmm_service: MMMServiceProtocol):
        """
        Test MMM service mocking with protocols.
        
        Shows how we can test complex MMM functionality without loading real models.
        """
        # Test model status
        status = mock_mmm_service.get_model_status()
        assert status.status == "loaded"
        assert status.model_loaded is True
        
        # Test model info
        info = mock_mmm_service.get_model_info()
        assert info.model_type == "Google Meridian (Mock)"
        assert info.data_source == "mock_data"
        assert len(info.channels) == 5
        
        # Test channel data
        channels = mock_mmm_service.get_channel_names()
        assert "Google_Search" in channels
        assert "Facebook" in channels
        
        # Test contribution data
        contribution_data = mock_mmm_service.get_contribution_data()
        assert "data" in contribution_data
        assert len(contribution_data["data"]) == 5  # 5 channels
        
        # Test specific channel
        google_data = mock_mmm_service.get_contribution_data("Google_Search")
        assert google_data["channel"] == "Google_Search"
        assert "data" in google_data
        assert "total_contribution" in google_data
    
    def test_error_handling_with_mocks(self, mock_mmm_service_no_model: MMMServiceProtocol):
        """
        Test error handling using mocks that simulate error conditions.
        
        This shows how protocols make it easy to test error scenarios.
        """
        from app.services.mmm_service import MMMModelError
        
        # Test model not loaded scenario
        status = mock_mmm_service_no_model.get_model_status()
        assert status.status == "not_found"
        assert status.model_loaded is False
        
        # Test that methods raise appropriate errors
        with pytest.raises(MMMModelError, match="Model not loaded"):
            mock_mmm_service_no_model.get_model_info()
        
        with pytest.raises(MMMModelError, match="Model not loaded"):
            mock_mmm_service_no_model.get_channel_names()
        
        with pytest.raises(MMMModelError, match="Model not loaded"):
            mock_mmm_service_no_model.get_contribution_data()


class TestProtocolFlexibility:
    """
    Test suite demonstrating the flexibility of protocol-based architecture.
    """
    
    def test_swappable_implementations(self):
        """
        Test that we can easily swap implementations without changing code.
        
        This is the core benefit of dependency inversion - we depend on
        abstractions, not concretions.
        """
        # Create two different user service implementations
        service1 = MockUserService()
        service2 = MockUserService()
        
        # They both implement the same protocol
        assert isinstance(service1, UserServiceProtocol)
        assert isinstance(service2, UserServiceProtocol)
        
        # We can use them interchangeably
        from app.schemas.user import UserCreate
        user_data = UserCreate(
            email="swap_test@example.com",
            password="test_password",
            full_name="Swap Test User"
        )
        
        # Create user in service1
        user1 = service1.create_user(user_data)
        assert user1.email == "swap_test@example.com"
        
        # Create user in service2 (different implementation, same interface)
        user_data.email = "swap_test2@example.com"
        user2 = service2.create_user(user_data)
        assert user2.email == "swap_test2@example.com"
        
        # Both services work the same way
        assert service1.get_users_count() != service2.get_users_count()  # Different instances
        assert len(service1.get_users()) != len(service2.get_users())  # Different data
    
    def test_protocol_type_checking(self):
        """
        Test that protocols provide proper type checking.
        
        This shows how protocols give us the benefits of static typing
        while maintaining flexibility.
        """
        # These should all be valid protocol implementations
        user_service: UserServiceProtocol = MockUserService()
        auth_service: AuthServiceProtocol = MockAuthService(user_service)
        mmm_service: MMMServiceProtocol = MockMMMService()
        
        # Test that they have the expected methods
        assert hasattr(user_service, 'get_user_by_email')
        assert hasattr(user_service, 'create_user')
        assert hasattr(auth_service, 'authenticate_user')
        assert hasattr(auth_service, 'login')
        assert hasattr(mmm_service, 'get_model_status')
        assert hasattr(mmm_service, 'get_channel_names')
        
        # Test that methods return expected types
        users = user_service.get_users()
        assert isinstance(users, list)
        
        status = mmm_service.get_model_status()
        from app.schemas.mmm import MMMStatus
        assert isinstance(status, MMMStatus)


class TestProtocolPerformance:
    """
    Test suite demonstrating performance benefits of protocol-based testing.
    """
    
    def test_fast_mock_operations(self, performance_mock_services):
        """
        Test that mock services are fast and don't have external dependencies.
        
        This shows how protocols enable fast, isolated testing.
        """
        import time
        
        user_service = performance_mock_services["user_service"]
        
        # Time user operations
        start_time = time.time()
        
        # Perform many operations
        for i in range(100):
            users = user_service.get_users(skip=i, limit=10)
            assert len(users) <= 10
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should be very fast (less than 1 second for 100 operations)
        assert elapsed < 1.0, f"Mock operations too slow: {elapsed:.3f}s"
    
    def test_no_external_dependencies(self, mock_user_service: UserServiceProtocol):
        """
        Test that mock services don't require external dependencies.
        
        This demonstrates how protocols enable true unit testing.
        """
        # These operations should work without any database, network, or file system
        users = mock_user_service.get_users()
        count = mock_user_service.get_users_count()
        
        # Should have predictable results
        assert len(users) == count
        assert count >= 2  # Default test users
        
        # Should be completely isolated
        from app.schemas.user import UserCreate
        user_data = UserCreate(
            email="isolation_test@example.com",
            password="test_password",
            full_name="Isolation Test"
        )
        
        new_user = mock_user_service.create_user(user_data)
        assert new_user.id is not None
        assert new_user.email == "isolation_test@example.com"


class TestProtocolIntegration:
    """
    Test suite demonstrating integration testing with protocols.
    """
    
    def test_full_authentication_flow(self, authenticated_client):
        """
        Test complete authentication flow using protocol-based mocks.
        
        This shows how protocols enable comprehensive integration testing
        without external dependencies.
        """
        client, token = authenticated_client
        
        # Test that we can access protected endpoints
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test user endpoints
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "admin@test.com"
        assert user_data["is_admin"] is True
        
        # Test MMM endpoints
        response = client.get("/api/v1/mmm/status", headers=headers)
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["status"] == "loaded"
        
        response = client.get("/api/v1/mmm/channels", headers=headers)
        assert response.status_code == 200
        
        channels_data = response.json()
        assert "channels" in channels_data
        assert len(channels_data["channels"]) == 5
    
    def test_permission_based_access(self, client_with_mocks: TestClient, regular_user_token: str):
        """
        Test permission-based access using protocol mocks.
        
        Shows how protocols make it easy to test different user roles.
        """
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        
        # Regular user should be able to access their own info
        response = client_with_mocks.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "user@test.com"
        assert user_data["is_admin"] is False
        
        # Regular user should NOT be able to access admin endpoints
        response = client_with_mocks.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403  # Forbidden
    
    def test_comprehensive_workflow(self, integration_test_setup, client_with_mocks: TestClient):
        """
        Test a comprehensive workflow using protocol-based architecture.
        
        This demonstrates the full power of dependency inversion for testing
        complex, multi-service workflows.
        """
        setup_data = integration_test_setup
        
        # Login as manager
        login_data = {
            "username": "manager@test.com",
            "password": "test_password"
        }
        
        response = client_with_mocks.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Manager should be able to see all users
        response = client_with_mocks.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200
        
        users_data = response.json()
        assert users_data["total"] == setup_data["total_users"]
        
        # Manager should be able to access MMM data
        response = client_with_mocks.get("/api/v1/mmm/info", headers=headers)
        assert response.status_code == 200
        
        info_data = response.json()
        assert info_data["model_type"] == "Google Meridian (Mock)"
        
        # Test MMM analysis workflow
        response = client_with_mocks.get("/api/v1/mmm/contribution", headers=headers)
        assert response.status_code == 200
        
        contribution_data = response.json()
        assert "data" in contribution_data
        
        # Test specific channel analysis
        response = client_with_mocks.get("/api/v1/mmm/contribution?channel=Google_Search", headers=headers)
        assert response.status_code == 200
        
        channel_data = response.json()
        assert channel_data["channel"] == "Google_Search"
