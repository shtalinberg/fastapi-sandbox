"""
Tests for Product CRUD and access control.
"""

import pytest
from httpx import AsyncClient

from fastapi import status

pytestmark = pytest.mark.asyncio

# Fixtures for test users, products, and client should be provided in conftest.py


async def test_create_product_admin(client: AsyncClient, admin_token: str):
    payload = {
        "title": "Test Product",
        "description": "Test desc",
        "price": 123.45,
        "external_id": "ext-1",
        "height": 10.0,
        "length": 20.0,
        "depth": 5.0,
    }
    response = await client.post(
        "/api/v1/products/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["external_id"] == payload["external_id"]


async def test_create_product_user_forbidden(client: AsyncClient, user_token: str):
    payload = {"title": "User Product", "price": 10.0}
    response = await client.post(
        "/api/v1/products/",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_products(client: AsyncClient):
    response = await client.get("/api/v1/products/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


async def test_get_product_by_id(client: AsyncClient, admin_token: str):
    # Create product first
    payload = {"title": "P1", "price": 1.0}
    create_resp = await client.post(
        "/api/v1/products/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    prod_id = create_resp.json()["id"]
    # Get by id
    response = await client.get(f"/api/v1/products/{prod_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == prod_id


async def test_update_product_admin(client: AsyncClient, admin_token: str):
    # Create product
    payload = {"title": "P2", "price": 2.0}
    create_resp = await client.post(
        "/api/v1/products/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    prod_id = create_resp.json()["id"]
    # Update
    update_payload = {"title": "P2-upd", "price": 3.0}
    response = await client.put(
        f"/api/v1/products/{prod_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "P2-upd"


async def test_delete_product_admin(client: AsyncClient, admin_token: str):
    # Create product
    payload = {"title": "P3", "price": 3.0}
    create_resp = await client.post(
        "/api/v1/products/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    prod_id = create_resp.json()["id"]
    # Delete
    response = await client.delete(
        f"/api/v1/products/{prod_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Check not found
    get_resp = await client.get(f"/api/v1/products/{prod_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
