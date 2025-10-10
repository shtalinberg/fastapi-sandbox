"""
Test configuration and fixtures for FastAPI application tests.
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dependencies import get_db
from main import main_app as app
from models.base import Base

# Імпортуємо всі моделі, щоб SQLAlchemy їх знав
from models.product import Product  # noqa: F401;
from models.user import User, UserRole
from services.auth import PasswordManager

# Test database settings
TEST_DATABASE_URL = (
    "postgresql+psycopg://fasandbox_user:fasandbox_pass@"
    "fasandbox_postgres:5432/fasandbox_db"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    # Create all tables before the test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a session for the test
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            # Clean up - rollback and close
            await session.rollback()

    # Clean up - drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Create a test client with dependency overrides."""

    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for authentication tests."""
    password_manager = PasswordManager()
    hashed_password = password_manager.hash_password("testpassword123")

    user = User(
        email="testuser@example.com",
        password=hashed_password,
        role=UserRole.USER,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Add plain password for testing
    user.plain_password = "testpassword123"
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession):
    """Create a test admin user."""
    password_manager = PasswordManager()
    hashed_password = password_manager.hash_password("adminpassword123")

    admin = User(
        email="testadmin@example.com",
        password=hashed_password,
        role=UserRole.ADMIN,
    )

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Add plain password for testing
    admin.plain_password = "adminpassword123"
    return admin


@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession):
    """Create an inactive test user."""
    password_manager = PasswordManager()
    hashed_password = password_manager.hash_password("inactivepassword123")

    user = User(
        email="inactive@example.com",
        password=hashed_password,
        role=UserRole.USER,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    user.plain_password = "inactivepassword123"
    return user


@pytest_asyncio.fixture
async def authenticated_user_headers(client: AsyncClient, test_user: User):
    """Get authorization headers for authenticated user."""
    login_data = {"email": test_user.email, "password": test_user.plain_password}

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    token = token_data["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_admin_headers(client: AsyncClient, test_admin: User):
    """Get authorization headers for authenticated admin."""
    login_data = {"email": test_admin.email, "password": test_admin.plain_password}

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    token = token_data["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {"email": "newuser@example.com", "password": "newpassword123"}


@pytest.fixture
def invalid_user_data():
    """Invalid user registration data for testing validation."""
    return {
        "email": "invalid-email",
        "password": "123",  # Too short
    }


# Utility functions for tests
async def create_multiple_users(db_session: AsyncSession, count: int = 5):
    """Create multiple test users for pagination tests."""
    password_manager = PasswordManager()
    users = []

    for i in range(count):
        user = User(
            email=f"user{i}@example.com",
            password=password_manager.hash_password(f"password{i}"),
            role=UserRole.USER,
        )
        users.append(user)
        db_session.add(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)

    return users


@pytest_asyncio.fixture
async def admin_token(authenticated_admin_headers):
    """Повертає лише токен-рядок для admin (без Bearer)."""
    header = authenticated_admin_headers["Authorization"]
    return header.split(" ", 1)[1]


@pytest_asyncio.fixture
async def user_token(authenticated_user_headers):
    """Повертає лише токен-рядок для user (без Bearer)."""
    header = authenticated_user_headers["Authorization"]
    return header.split(" ", 1)[1]
