#!/usr/bin/env python3
"""
Database seeding script for development and testing.

Seeds test users for authentication and development.

Usage:
    python seed.py [--force] [--quiet]
    
Or via pnpm:
    pnpm seed
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database and models
from sqlalchemy import select
from app.core.database import SessionLocal, init_db
from app.models import User
from app.core.security import hash_password
from app.core.logging import get_logger

# Get logger
logger = get_logger(__name__)


def get_sample_users() -> List[Dict[str, Any]]:
    """Get sample user data for seeding."""
    return [
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


def seed_users(force: bool = False, quiet: bool = False) -> int:
    """Seed sample users for development and testing.
    
    Args:
        force: Skip existing user checks and recreate all users
        quiet: Suppress non-error output
        
    Returns:
        Number of users created
    """
    sample_users = get_sample_users()
    
    if not quiet:
        logger.info("Seeding users...")
    
    created_count = 0
    
    # Create database session
    with SessionLocal() as db:
        try:
            for user_data in sample_users:
                if not quiet:
                    logger.info(f"Processing user: {user_data['email']}")
                
                # Check if user already exists (unless force is True)
                if not force:
                    result = db.execute(
                        select(User).filter(User.email == user_data['email'])
                    )
                    existing_user = result.scalar_one_or_none()
                    if existing_user:
                        if not quiet:
                            logger.info(f"User {user_data['email']} already exists, skipping")
                        continue
                else:
                    # Force mode: delete existing user first
                    result = db.execute(
                        select(User).filter(User.email == user_data['email'])
                    )
                    existing_user = result.scalar_one_or_none()
                    if existing_user:
                        db.delete(existing_user)
                        if not quiet:
                            logger.info(f"Deleted existing user: {user_data['email']}")
                
                # Create new user
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
                created_count += 1
                
                if not quiet:
                    logger.info(f"Created user: {user_data['email']}")
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating users: {e}")
            raise
    
    if not quiet:
        logger.info(f"Successfully created {created_count} users")
    
    return created_count


def main() -> None:
    """Main seeding function with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="Seed database with test users for development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python seed.py                    # Normal seeding (skip existing users)
    python seed.py --force            # Recreate all users
    python seed.py --quiet            # Suppress output
    python seed.py --force --quiet    # Silent recreation
        """
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Recreate users even if they already exist"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Suppress non-error output"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        logger.info("Starting database seeding...")
        logger.info("=" * 50)
    
    try:
        # Initialize database tables
        init_db()
        if not args.quiet:
            logger.info("Database tables initialized")
        
        # Seed users
        created_count = seed_users(force=args.force, quiet=args.quiet)
        
        if not args.quiet:
            logger.info("=" * 50)
            logger.info("Database seeding completed successfully!")
            
            if created_count > 0:
                logger.info("Test login credentials:")
                sample_users = get_sample_users()
                for user in sample_users:
                    logger.info(f"  {user['email']} / {user['password']}")
            else:
                logger.info("No new users created (use --force to recreate existing users)")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
