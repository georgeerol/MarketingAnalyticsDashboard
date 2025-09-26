"""
Protocol-based test fixtures demonstrating the power of dependency inversion.

These fixtures show how easy it is to test with protocols - we can swap out
any service implementation without changing the tests.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import Depends

from app.main import app
from app.services.interfaces import UserServiceProtocol, AuthServiceProtocol, MMMServiceProtocol
from tests.mocks import MockUserService, MockAuthService, MockMMMService


@pytest.fixture
def mock_user_service() -> UserServiceProtocol:
    """
    Provide a mock user service that implements UserServiceProtocol.
    
    This fixture demonstrates how protocols make testing simple - any test
    can use this fixture and get a clean, predictable user service.
    """
    return MockUserService()


@pytest.fixture
def mock_auth_service(mock_user_service: UserServiceProtocol) -> AuthServiceProtocol:
    """
    Provide a mock auth service that implements AuthServiceProtocol.
    
    Notice how this depends on UserServiceProtocol, not a concrete class.
    This is dependency inversion in action!
    """
    return MockAuthService(mock_user_service)


@pytest.fixture
def mock_mmm_service() -> MMMServiceProtocol:
    """
    Provide a mock MMM service that implements MMMServiceProtocol.
    
    This fixture can simulate different model states for comprehensive testing.
    """
    return MockMMMService(simulate_model_loaded=True)


@pytest.fixture
def mock_mmm_service_no_model() -> MMMServiceProtocol:
    """
    Provide a mock MMM service with no model loaded.
    
    Useful for testing error conditions and model loading scenarios.
    """
    return MockMMMService(simulate_model_loaded=False)


@pytest.fixture
def client_with_mocks(
    mock_user_service: UserServiceProtocol,
    mock_auth_service: AuthServiceProtocol,
    mock_mmm_service: MMMServiceProtocol
) -> TestClient:
    """
    Provide a FastAPI test client with all services mocked.
    
    This demonstrates the ultimate power of dependency inversion - we can
    replace ALL services with mocks and test the entire API without any
    external dependencies!
    """
    from app.api.deps import get_user_service, get_auth_service, get_mmm_service
    
    # Override dependencies with our mocks
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    app.dependency_overrides[get_mmm_service] = lambda: mock_mmm_service
    
    client = TestClient(app)
    
    yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client_with_mocks: TestClient, mock_auth_service: AuthServiceProtocol) -> tuple[TestClient, str]:
    """
    Provide an authenticated test client with a valid token.
    
    Returns a tuple of (client, token) for easy authenticated testing.
    """
    # Login to get a token
    login_data = {
        "username": "admin@test.com",
        "password": "admin_password"
    }
    
    response = client_with_mocks.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    
    return client_with_mocks, token


@pytest.fixture
def admin_user_token(mock_user_service: UserServiceProtocol, mock_auth_service: AuthServiceProtocol) -> str:
    """
    Provide a token for an admin user.
    
    Useful for testing admin-only endpoints.
    """
    admin_user = mock_user_service.get_user_by_email("admin@test.com")
    assert admin_user is not None
    return mock_auth_service.create_mock_token_for_user(admin_user)


@pytest.fixture
def regular_user_token(mock_user_service: UserServiceProtocol, mock_auth_service: AuthServiceProtocol) -> str:
    """
    Provide a token for a regular user.
    
    Useful for testing regular user permissions.
    """
    regular_user = mock_user_service.get_user_by_email("user@test.com")
    assert regular_user is not None
    return mock_auth_service.create_mock_token_for_user(regular_user)


# Performance testing fixtures
@pytest.fixture
def performance_mock_services():
    """
    Provide mock services optimized for performance testing.
    
    These mocks can simulate various performance characteristics.
    """
    user_service = MockUserService()
    auth_service = MockAuthService(user_service)
    mmm_service = MockMMMService()
    
    # Add more test data for performance testing
    for i in range(100):
        user_service.add_test_user(
            email=f"perf_user_{i}@test.com",
            full_name=f"Performance User {i}"
        )
    
    return {
        "user_service": user_service,
        "auth_service": auth_service,
        "mmm_service": mmm_service
    }


# Error simulation fixtures
@pytest.fixture
def error_simulation_services():
    """
    Provide services that can simulate various error conditions.
    
    Useful for testing error handling and resilience.
    """
    class ErrorSimulatingUserService(MockUserService):
        def __init__(self):
            super().__init__()
            self.should_error = False
            self.error_message = "Simulated error"
        
        def get_user_by_email(self, email: str):
            if self.should_error:
                raise Exception(self.error_message)
            return super().get_user_by_email(email)
        
        def simulate_error(self, should_error: bool = True, message: str = "Simulated error"):
            self.should_error = should_error
            self.error_message = message
    
    user_service = ErrorSimulatingUserService()
    auth_service = MockAuthService(user_service)
    mmm_service = MockMMMService()
    
    return {
        "user_service": user_service,
        "auth_service": auth_service,
        "mmm_service": mmm_service
    }


# Integration testing fixtures
@pytest.fixture
def integration_test_setup(mock_user_service: UserServiceProtocol):
    """
    Set up a comprehensive test environment for integration testing.
    
    Creates a realistic set of test data across all services.
    """
    # Add various types of users
    mock_user_service.add_test_user("manager@test.com", "Test Manager", is_admin=True)
    mock_user_service.add_test_user("analyst@test.com", "Test Analyst")
    mock_user_service.add_test_user("viewer@test.com", "Test Viewer")
    
    # Add inactive user
    inactive_user = mock_user_service.add_test_user("inactive@test.com", "Inactive User")
    mock_user_service.deactivate_user(inactive_user.id)
    
    return {
        "total_users": mock_user_service.get_users_count(),
        "active_users": mock_user_service.get_users_count(active_only=True),
        "admin_users": len([u for u in mock_user_service.get_users(active_only=False) if u.is_admin])
    }
