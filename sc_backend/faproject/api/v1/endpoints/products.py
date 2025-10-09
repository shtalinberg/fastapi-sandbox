"""
Products API endpoints.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from dependencies import get_db

router = APIRouter()


@router.get("/", summary="Get all products")
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    # Placeholder for now - will implement with models later
    return {
        "message": "Products endpoint working",
        "skip": skip,
        "limit": limit,
        "data": []
    }


@router.get("/{product_id}", summary="Get product by ID")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID.
    """
    # Placeholder for now
    return {
        "message": f"Product {product_id} details",
        "product_id": product_id
    }


@router.post("/", summary="Create new product", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    Admin only endpoint.
    """
    # Placeholder for now
    return {
        "message": "Product created successfully",
        "id": 1
    }