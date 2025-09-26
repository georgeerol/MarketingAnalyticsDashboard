"""
Reset database tables - drop and recreate all tables.
"""

import asyncio
from app.core.database import Base, async_engine

async def reset_database():
    """Drop and recreate all database tables."""
    print("Dropping all tables...")
    
    async with async_engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import User, ResponseCurve, MMMModelData
        
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped.")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("All tables created.")
    
    print("Database reset completed!")

if __name__ == "__main__":
    asyncio.run(reset_database())
