"""
Test configuration and fixtures for the MMM Dashboard API.
"""

import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import get_db, Base
from models import User
from auth_utils import hash_password
from mmm_utils import MMMModelLoader

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    def _override_get_db():
        return db_session
    return _override_get_db

@pytest.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def test_client() -> TestClient:
    """Create a synchronous test client for simple tests."""
    return TestClient(app)

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        company="Test Company",
        role="user",
        hashed_password=hash_password("testpassword123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def mmm_model_path() -> Path:
    """Path to the real MMM model file."""
    return Path(__file__).parent.parent / "data" / "models" / "saved_mmm.pkl"

@pytest.fixture
def mmm_loader() -> MMMModelLoader:
    """Create an MMM model loader instance."""
    return MMMModelLoader()

@pytest.fixture
def mock_mmm_loader() -> MMMModelLoader:
    """Create an MMM model loader with mock data."""
    return MMMModelLoader(use_mock_data=True)

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for API requests."""
    from auth_utils import create_access_token
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
