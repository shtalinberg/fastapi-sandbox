"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

# Create async SQLAlchemy engine
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Create sync engine for non-async operations (if needed)
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create SessionLocal class for sync operations (if needed)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
