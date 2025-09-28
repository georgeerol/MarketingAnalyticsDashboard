#!/usr/bin/env python3
"""
Reset database tables - drop and recreate all tables.

WARNING: This script will permanently delete all data in the database!
Use with extreme caution.

Usage:
    python reset_db.py [--force] [--quiet]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine, SessionLocal
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def confirm_reset(force: bool = False) -> bool:
    """Confirm the database reset operation."""
    if force:
        logger.warning("Force flag provided - skipping confirmation")
        return True
    
    print("\n" + "="*60)
    print("⚠️  DATABASE RESET WARNING ⚠️")
    print("="*60)
    print("This operation will:")
    print("  • DROP all existing tables")
    print("  • DELETE all data permanently")
    print("  • RECREATE empty tables")
    print("="*60)
    print()
    
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    return response.strip() == "YES"


def reset_database(quiet: bool = False) -> None:
    """Drop and recreate all database tables."""
    try:
        if not quiet:
            logger.info("Starting database reset...")
        
        # Import all models to ensure they are registered
        from app.models import User  # This triggers all model imports
        
        if not quiet:
            logger.info("Dropping all tables...")
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        if not quiet:
            logger.info("All tables dropped successfully")
            logger.info("Creating all tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        if not quiet:
            logger.info("All tables created successfully")
            logger.info("Database reset completed!")
        
        # Verify the reset worked
        with SessionLocal() as db:
            # Try a simple query to verify connection
            db.execute("SELECT 1")
            if not quiet:
                logger.info("Database connection verified")
                
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        logger.error("Please check your database connection and try again")
        sys.exit(1)


def main() -> None:
    """Main function to handle CLI and run database reset."""
    parser = argparse.ArgumentParser(
        description="Reset database tables (WARNING: Destructive operation!)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python reset_db.py                    # Interactive confirmation
    python reset_db.py --force            # Skip confirmation
    python reset_db.py --force --quiet    # Silent reset
        """
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Skip confirmation prompt (DANGEROUS!)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Suppress output messages"
    )
    
    args = parser.parse_args()
    
    # Confirm the operation
    if not confirm_reset(args.force):
        if not args.quiet:
            print("Database reset cancelled.")
        sys.exit(0)
    
    # Perform the reset
    reset_database(args.quiet)


if __name__ == "__main__":
    main()
