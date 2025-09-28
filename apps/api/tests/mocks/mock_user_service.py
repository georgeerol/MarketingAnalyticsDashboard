"""
Mock implementation of UserServiceProtocol for testing.

This demonstrates how easy it is to create test doubles when using protocols.
"""

from typing import Optional, Dict
from app.services.interfaces import UserServiceProtocol
from app.schemas.user import UserCreate
from app.models.user import User


class MockUser:
    """Simple mock user model for testing."""
    
    def __init__(self, id: int, email: str, full_name: str, hashed_password: str = "mock_hash", is_active: bool = True, is_admin: bool = False):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_admin = is_admin
        self.role = "admin" if is_admin else "user"
        self.company = None
        self.created_at = "2024-01-01T00:00:00"
        self.updated_at = "2024-01-01T00:00:00"


class MockUserService(UserServiceProtocol):
    """
    Mock implementation of UserServiceProtocol.
    
    Provides predictable, controllable behavior for testing without database dependencies.
    """
    
    def __init__(self):
        self.users: Dict[int, MockUser] = {}
        self.next_id = 1
        self.email_index: Dict[str, int] = {}
        
        # Add some default test users
        self._add_default_users()
    
    def _add_default_users(self):
        """Add some default users for testing."""
        admin_user = MockUser(
            id=1,
            email="admin@test.com",
            full_name="Test Admin",
            is_admin=True
        )
        self.users[1] = admin_user
        self.email_index["admin@test.com"] = 1
        
        regular_user = MockUser(
            id=2,
            email="user@test.com", 
            full_name="Test User"
        )
        self.users[2] = regular_user
        self.email_index["user@test.com"] = 2
        
        self.next_id = 3
    
    def get_user_by_id(self, user_id: int) -> Optional[MockUser]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[MockUser]:
        """Get user by email address."""
        user_id = self.email_index.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def create_user(self, user_data: UserCreate) -> MockUser:
        """Create a new user."""
        # Check if email already exists
        if user_data.email in self.email_index:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Create new user
        user = MockUser(
            id=self.next_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password="mock_hashed_password"
        )
        
        # Store user
        self.users[self.next_id] = user
        self.email_index[user_data.email] = self.next_id
        self.next_id += 1
        
        return user
    
    # Utility methods for testing
    def clear_users(self):
        """Clear all users (useful for test setup)."""
        self.users.clear()
        self.email_index.clear()
        self.next_id = 1
    
    def add_test_user(self, email: str, full_name: str, is_admin: bool = False) -> MockUser:
        """Add a test user with specific properties."""
        user_data = UserCreate(
            email=email,
            password="test_password",
            full_name=full_name
        )
        user = self.create_user(user_data)
        user.is_admin = is_admin
        return user
