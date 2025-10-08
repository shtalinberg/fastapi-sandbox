import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.crud.user import create_user
from app.schemas.user import UserCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestClient(app)
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_user(db):
    user_data = UserCreate(username="admin", email="admin@example.com", password="admin123")
    return create_user(db, user_data, is_admin=True)


@pytest.fixture
def regular_user(db):
    user_data = UserCreate(username="user", email="user@example.com", password="user123")
    return create_user(db, user_data, is_admin=False)


@pytest.fixture
def admin_token(client):
    # Register and login admin
    client.post("/api/v1/auth/register", json={
        "username": "testadmin",
        "email": "testadmin@example.com",
        "password": "admin123"
    })
    # Make admin manually (in real scenario, this would be done via a separate endpoint)
    db = TestingSessionLocal()
    from app.crud.user import get_user_by_username
    user = get_user_by_username(db, "testadmin")
    user.is_admin = True
    db.commit()
    db.close()
    
    response = client.post("/api/v1/auth/login", data={
        "username": "testadmin",
        "password": "admin123"
    })
    return response.json()["access_token"]


@pytest.fixture
def user_token(client):
    # Register and login regular user
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "user123"
    })
    
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "user123"
    })
    return response.json()["access_token"]
