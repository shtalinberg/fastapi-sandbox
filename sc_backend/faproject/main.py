"""
FastAPI main application module.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import api_router
from core.config import settings

# Create FastAPI app
main_app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "REST API service with JWT authentication, product management and "
        "background synchronization"
    ),
    version="0.1.0",
    debug=settings.DEBUG,
    openapi_url=(f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None),
)

# Add CORS middleware
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
main_app.include_router(api_router, prefix=settings.API_V1_STR)


@main_app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "message": "FastAPI Sandbox is running!",
        "project": settings.PROJECT_NAME,
        "debug": settings.DEBUG,
        "docs_url": "/docs" if settings.DEBUG else None,
    }


@main_app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and Docker health checks.
    """
    return {"status": "healthy", "project": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:main_app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
