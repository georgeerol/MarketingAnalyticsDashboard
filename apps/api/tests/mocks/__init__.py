"""
Mock implementations for testing with protocols.

This module provides clean, simple mock implementations of our service protocols,
demonstrating the power of dependency inversion for testing.
"""

from tests.mocks.mock_user_service import MockUserService
from tests.mocks.mock_auth_service import MockAuthService
from tests.mocks.mock_mmm_service import MockMMMService

__all__ = [
    "MockUserService",
    "MockAuthService", 
    "MockMMMService",
]
