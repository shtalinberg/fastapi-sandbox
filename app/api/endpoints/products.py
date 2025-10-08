from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.crud.product import (
    get_product,
    get_products,
    create_product,
    update_product,
    delete_product
)
from app.core.deps import get_current_admin_user, get_optional_user

router = APIRouter()


@router.get("/", response_model=List[Product])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get list of products.
    Accessible to all users (authenticated and anonymous).
    """
    products = get_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get a specific product by ID.
    Accessible to all users (authenticated and anonymous).
    """
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Create a new product.
    Only accessible to administrators.
    """
    return create_product(db=db, product=product)


@router.put("/{product_id}", response_model=Product)
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Update an existing product.
    Only accessible to administrators.
    """
    db_product = update_product(db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Delete a product.
    Only accessible to administrators.
    """
    db_product = delete_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
