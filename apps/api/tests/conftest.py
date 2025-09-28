"""
Test configuration and fixtures for the MMM Dashboard API.
"""

import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from new refactored structure
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.core.security import hash_password
from app.services.mmm_service import MMMService

# Test database URL - use sync SQLite for testing to match production sync services
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine (sync to match production)
from sqlalchemy import create_engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = sessionmaker(
    test_engine,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create a test database session."""
    Base.metadata.create_all(bind=test_engine)
    
    with TestSessionLocal() as session:
        yield session
    
    Base.metadata.drop_all(bind=test_engine)


@pytest_asyncio.fixture
async def client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def test_client() -> TestClient:
    """Create a synchronous test client for simple tests."""
    return TestClient(app)

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        company="Test Company",
        role="user",
        hashed_password=hash_password("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def mmm_model_path() -> Path:
    """Path to the real MMM model file."""
    return Path(__file__).parent.parent / "data" / "models" / "saved_mmm.pkl"

@pytest.fixture
def mmm_service() -> MMMService:
    """Create an MMM service instance."""
    return MMMService()

@pytest.fixture
def mmm_service_with_fallback() -> MMMService:
    """Create an MMM service for testing (will use real model if available)."""
    return MMMService()

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for API requests."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

# Test data fixtures
@pytest.fixture
def sample_contribution_data():
    """Sample contribution data for testing."""
    return {
        "Channel_1": [1000, 1100, 1200, 1050, 1300],
        "Channel_2": [800, 850, 900, 920, 950],
        "Channel_3": [600, 650, 700, 680, 720],
        "Channel_4": [400, 420, 450, 430, 460],
        "Channel_5": [300, 320, 340, 330, 350]
    }

@pytest.fixture
def sample_response_curves():
    """Sample response curve data for testing."""
    return {
        "curves": {
            "Channel_1": {
                "spend": [0, 10, 20, 30, 40, 50],
                "response": [0, 8, 15, 21, 26, 30],
                "saturation_point": 45,
                "efficiency": 0.75
            },
            "Channel_2": {
                "spend": [0, 10, 20, 30, 40, 50],
                "response": [0, 7, 13, 18, 22, 25],
                "saturation_point": 40,
                "efficiency": 0.65
            }
        }
    }

# Service fixtures for testing business logic
@pytest.fixture
def user_service(db_session: Session):
    """Create a user service instance for testing."""
    from app.services.user_service import UserService
    return UserService(db_session)

@pytest.fixture
def auth_service(db_session: Session):
    """Create an auth service instance for testing."""
    from app.services.auth_service import AuthService
    return AuthService(db_session)