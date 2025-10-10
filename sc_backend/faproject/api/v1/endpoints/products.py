"""
Products API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user
from tasks.sync_products import sync_products_task
from models.user import User
from schemas.product import ProductCreate, ProductUpdate, ProductPublic
from services.product import ProductService

router = APIRouter()


@router.post("/sync", status_code=200, summary="Manual product sync (admin only)")
async def sync_products_manual(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Admin only")
    sync_products_task.delay()
    return {"status": "celery sync started"}


@router.get("/", response_model=List[ProductPublic], summary="Get all products")
async def get_products(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    products = await service.list_products(skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductPublic, summary="Get product by ID")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_product(product_id)
    return product


@router.post(
    "/",
    response_model=ProductPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product",
)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.create_product(product_in, current_user)
    return product


@router.put("/{product_id}", response_model=ProductPublic, summary="Update product")
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.update_product(product_id, product_in, current_user)
    return product


@router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete product"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    await service.delete_product(product_id, current_user)
    return None
