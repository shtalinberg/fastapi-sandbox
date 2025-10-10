"""
Main API v1 router that aggregates all endpoints.
"""

from fastapi import APIRouter

from api.auth import router as auth_router
from api.users import router as users_router

from api.v1.endpoints import products

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router)

# Include user management routes
api_router.include_router(users_router)

api_router.include_router(products.router, prefix="/products", tags=["products"])
