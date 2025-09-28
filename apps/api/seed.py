"""
Database seeding script for development and testing.

Seeds test users for authentication and development.

Usage:
    python seed.py
    
Or via pnpm:
    pnpm seed
"""

import sys
from pathlib import Path
# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

# Import database and models
from sqlalchemy import select
from app.core.database import SessionLocal, init_db
from app.models import User
from app.core.security import hash_password
from app.core.logging import get_logger

# Get logger
logger = get_logger(__name__)


def seed_users() -> None:
    """Seed sample users for development and testing."""
    
    sample_users = [
        {
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
            "role": "user",
            "is_active": True,
            "company": "Test Corp"
        },
        {
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": "admin",
            "is_active": True,
            "company": "Demo Corp"
        },
        {
            "email": "demo@example.com",
            "password": "demo123", 
            "full_name": "Demo User",
            "role": "user",
            "is_active": True,
            "company": "Demo Corp"
        },
        {
            "email": "marketer@example.com",
            "password": "marketer123",
            "full_name": "Marketing Manager",
            "role": "user", 
            "is_active": True,
            "company": "Marketing Agency"
        },
        {
            "email": "analyst@example.com",
            "password": "analyst123",
            "full_name": "Data Analyst",
            "role": "user",
            "is_active": True,
            "company": "Analytics Firm"
        }
    ]
    
    logger.info("Seeding users...")
    
    # Create database session
    with SessionLocal() as db:
        try:
            for user_data in sample_users:
                logger.info(f"Creating user: {user_data['email']}")
                
                # Check if user already exists
                result = db.execute(
                    select(User).filter(User.email == user_data['email'])
                )
                existing_user = result.scalar_one_or_none()
                if existing_user:
                    logger.info(f"User {user_data['email']} already exists, skipping")
                    continue
                
                hashed_password = hash_password(user_data['password'])
                user = User(
                    email=user_data['email'],
                    hashed_password=hashed_password,
                    full_name=user_data['full_name'],
                    role=user_data['role'],
                    is_active=user_data['is_active'],
                    company=user_data['company']
                )
                db.add(user)
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating users: {e}")
            raise
    
    logger.info(f"Created {len(sample_users)} users")


def main() -> None:
    """Main seeding function."""
    
    logger.info("Starting database seeding...")
    logger.info("=" * 50)
    
    try:
        # Initialize database tables
        init_db()
        logger.info("Database tables initialized")
        
        # Seed users
        seed_users()
        
        logger.info("=" * 50)
        logger.info("Database seeding completed successfully!")
        logger.info("Test login credentials:")
        logger.info("  test@example.com / test123")
        logger.info("  admin@example.com / admin123")
        logger.info("  demo@example.com / demo123")
        logger.info("  marketer@example.com / marketer123")
        logger.info("  analyst@example.com / analyst123")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        raise


if __name__ == "__main__":
    main()
