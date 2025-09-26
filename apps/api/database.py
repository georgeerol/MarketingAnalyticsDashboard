from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import get_settings

settings = get_settings()

# Database connection - using psycopg2 (which we installed)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
