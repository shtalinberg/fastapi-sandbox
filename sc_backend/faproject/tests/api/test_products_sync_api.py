import pytest
import pytest_asyncio
from main import main_app as app
from models.user import User, UserRole
from services.auth import JWTManager, PasswordManager
import httpx
from httpx import ASGITransport


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token_header(db_session):
    password = PasswordManager.hash_password("adminpass123")
    admin = User(email="admin@sync.test", password=password, role=UserRole.ADMIN)
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    token = JWTManager.create_access_token(
        {"sub": str(admin.id), "email": admin.email, "role": admin.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def user_token_header(db_session):
    password = PasswordManager.hash_password("userpass123")
    user = User(email="user@sync.test", password=password, role=UserRole.USER)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = JWTManager.create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_sync_products_manual_admin(
    async_client, admin_token_header, monkeypatch
):
    from tasks import sync_products

    called = {}

    def fake_delay():
        called["run"] = True

    monkeypatch.setattr(sync_products.sync_products_task, "delay", fake_delay)

    response = await async_client.post(
        "/api/v1/products/sync", headers=admin_token_header
    )
    assert response.status_code == 200
    assert response.json()["status"].startswith("celery sync started")
    assert called["run"]


@pytest.mark.asyncio
async def test_sync_products_manual_user_forbidden(async_client, user_token_header):
    response = await async_client.post(
        "/api/v1/products/sync", headers=user_token_header
    )
    assert response.status_code == 403
