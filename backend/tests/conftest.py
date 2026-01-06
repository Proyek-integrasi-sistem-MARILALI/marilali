"""
Pytest configuration and fixtures for API testing
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.main import app
from src.database import get_db
from src.models import Base
from src.config import settings


# Test database URL (use existing database or create test-specific one)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    # Cleanup after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(client: AsyncClient) -> dict:
    """Create a test user and return credentials"""
    import time
    user_data = {
        "name": "Test User",
        "email": f"test_{int(time.time() * 1000)}@example.com",  # Unique email
        "password": "TestPass123!"
    }
    
    # Register user
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    return {
        **user_data,
        "user_id": response.json()["id"]
    }


@pytest.fixture(scope="function")
async def auth_token(client: AsyncClient, test_user: dict) -> str:
    """Get authentication token for test user"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
async def auth_headers(auth_token: str) -> dict:
    """Get authorization headers with token"""
    return {"Authorization": f"Bearer {auth_token}"}


# Markers for test categories
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "ai: AI recommendation tests")
    config.addinivalue_line("markers", "itinerary: Itinerary tests")
    config.addinivalue_line("markers", "review: Review tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
