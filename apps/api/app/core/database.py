"""
Database configuration and session management.
"""

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# Create sync engine for migrations and sync operations
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async engine for application
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+psycopg://", "postgresql+psycopg://"
)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session makers
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session for sync operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for async operations."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import user, campaign, mmm
        await conn.run_sync(Base.metadata.create_all)
