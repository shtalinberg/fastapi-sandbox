def test_create_product_as_admin(client, admin_token):
    response = client.post(
        "/api/v1/products/",
        json={
            "title": "Test Product",
            "price": 99.99,
            "description": "A test product",
            "category": "test"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Product"
    assert data["price"] == 99.99


def test_create_product_as_regular_user(client, user_token):
    response = client.post(
        "/api/v1/products/",
        json={
            "title": "Test Product",
            "price": 99.99,
            "description": "A test product"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


def test_create_product_anonymous(client):
    response = client.post(
        "/api/v1/products/",
        json={
            "title": "Test Product",
            "price": 99.99,
            "description": "A test product"
        }
    )
    assert response.status_code == 401


def test_list_products_anonymous(client, admin_token):
    # Create a product first
    client.post(
        "/api/v1/products/",
        json={
            "title": "Test Product",
            "price": 99.99,
            "description": "A test product"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # List products without auth
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Product"


def test_get_product_anonymous(client, admin_token):
    # Create a product first
    create_response = client.post(
        "/api/v1/products/",
        json={
            "title": "Test Product",
            "price": 99.99,
            "description": "A test product"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    product_id = create_response.json()["id"]
    
    # Get product without auth
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Product"


def test_update_product_as_admin(client, admin_token):
    # Create a product first
    create_response = client.post(
        "/api/v1/products/",
        json={
            "title": "Original Product",
            "price": 99.99
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    product_id = create_response.json()["id"]
    
    # Update product
    response = client.put(
        f"/api/v1/products/{product_id}",
        json={"title": "Updated Product"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Product"


def test_delete_product_as_admin(client, admin_token):
    # Create a product first
    create_response = client.post(
        "/api/v1/products/",
        json={
            "title": "Product to Delete",
            "price": 99.99
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    product_id = create_response.json()["id"]
    
    # Delete product
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204
    
    # Verify product is deleted
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404
