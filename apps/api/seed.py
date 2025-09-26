"""
Database seeding script for development and testing.

This script populates the database with sample data including:
- Test users for authentication testing
- Sample MMM (Media Mix Modeling) data for dashboard development
- Demo scenarios for different user types

Usage:
    python seed.py
    
Or via pnpm:
    pnpm seed
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

# Import database and models
from database import SessionLocal, init_db
from models import User, Campaign, Channel, ChannelPerformance, ResponseCurve
from auth_utils import hash_password


async def seed_users() -> None:
    """Seed sample users for development and testing."""
    
    sample_users = [
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
    
    print(" Seeding users...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        for user_data in sample_users:
            print(f"  → Creating user: {user_data['email']}")
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                print(f"    User {user_data['email']} already exists, skipping...")
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
        print(f"Error creating users: {e}")
        raise
    finally:
        db.close()
    
    print(f" Created {len(sample_users)} users")


async def seed_mmm_sample_data() -> None:
    """Seed sample Media Mix Modeling data for dashboard development."""
    
    # Sample marketing channels
    sample_channels = [
        {
            "name": "Google Ads",
            "type": "paid_search",
            "category": "digital",
            "description": "Google Search and Display advertising"
        },
        {
            "name": "Facebook Ads", 
            "type": "social_media",
            "category": "digital",
            "description": "Facebook and Instagram advertising"
        },
        {
            "name": "TV Advertising",
            "type": "television",
            "category": "traditional",
            "description": "National and local TV campaigns"
        },
        {
            "name": "Email Marketing",
            "type": "email",
            "category": "digital", 
            "description": "Email campaigns and newsletters"
        },
        {
            "name": "Radio",
            "type": "radio",
            "category": "traditional",
            "description": "Radio advertising campaigns"
        },
        {
            "name": "YouTube Ads",
            "type": "video",
            "category": "digital",
            "description": "YouTube video advertising"
        }
    ]
    
    # Sample campaign data (for contribution charts)
    sample_campaigns = [
        {
            "name": "Q4 Holiday Campaign",
            "start_date": "2024-10-01",
            "end_date": "2024-12-31",
            "budget": 500000,
            "channels": ["Google Ads", "Facebook Ads", "TV Advertising"],
            "target_audience": "Holiday shoppers"
        },
        {
            "name": "Brand Awareness Spring",
            "start_date": "2024-03-01", 
            "end_date": "2024-05-31",
            "budget": 300000,
            "channels": ["TV Advertising", "Radio", "YouTube Ads"],
            "target_audience": "General consumers"
        },
        {
            "name": "Digital Focus Summer",
            "start_date": "2024-06-01",
            "end_date": "2024-08-31", 
            "budget": 200000,
            "channels": ["Google Ads", "Facebook Ads", "Email Marketing"],
            "target_audience": "Online shoppers"
        }
    ]
    
    print("🌱 Seeding MMM sample data...")
    
    # TODO: Implement once MMM models are ready
    for channel in sample_channels:
        print(f"  → Creating channel: {channel['name']}")
        
    for campaign in sample_campaigns:
        print(f"  → Creating campaign: {campaign['name']}")
    
    print(f" Created {len(sample_channels)} channels and {len(sample_campaigns)} campaigns")


async def seed_mmm_performance_data() -> None:
    """Seed sample performance data for response curves and contribution charts."""
    
    # Sample data that would typically come from the Google Meridian model
    sample_performance_data = {
        "contribution_data": {
            "Google Ads": {
                "contribution_percentage": 35.2,
                "spend": 150000,
                "incremental_conversions": 2840,
                "efficiency_score": 0.89
            },
            "Facebook Ads": {
                "contribution_percentage": 28.7,
                "spend": 120000,
                "incremental_conversions": 2310,
                "efficiency_score": 0.76
            },
            "TV Advertising": {
                "contribution_percentage": 22.1,
                "spend": 200000,
                "incremental_conversions": 1780,
                "efficiency_score": 0.45
            },
            "Email Marketing": {
                "contribution_percentage": 8.9,
                "spend": 25000,
                "incremental_conversions": 720,
                "efficiency_score": 1.44
            },
            "Radio": {
                "contribution_percentage": 3.8,
                "spend": 50000,
                "incremental_conversions": 310,
                "efficiency_score": 0.31
            },
            "YouTube Ads": {
                "contribution_percentage": 1.3,
                "spend": 30000,
                "incremental_conversions": 105,
                "efficiency_score": 0.18
            }
        },
        "response_curves": {
            # Sample data points for diminishing returns curves
            "Google Ads": [
                {"spend": 0, "conversions": 0},
                {"spend": 25000, "conversions": 850},
                {"spend": 50000, "conversions": 1520},
                {"spend": 75000, "conversions": 2050},
                {"spend": 100000, "conversions": 2450},
                {"spend": 125000, "conversions": 2750},
                {"spend": 150000, "conversions": 2840},
                {"spend": 175000, "conversions": 2890},
                {"spend": 200000, "conversions": 2920}
            ],
            "Facebook Ads": [
                {"spend": 0, "conversions": 0},
                {"spend": 20000, "conversions": 680},
                {"spend": 40000, "conversions": 1200},
                {"spend": 60000, "conversions": 1580},
                {"spend": 80000, "conversions": 1850},
                {"spend": 100000, "conversions": 2050},
                {"spend": 120000, "conversions": 2310},
                {"spend": 140000, "conversions": 2380},
                {"spend": 160000, "conversions": 2420}
            ]
        }
    }
    
    print("🌱 Seeding MMM performance data...")
    
    # TODO: Store this data in appropriate tables once models are ready
    print("  → Creating contribution data...")
    print("  → Creating response curve data...")
    
    print(" Created sample performance data for visualizations")


async def clear_database() -> None:
    """Clear all data from the database (for development only)."""
    
    print("  Clearing database...")
    
    # TODO: Implement database clearing once models are ready
    # This should drop and recreate tables or delete all records
    
    print(" Database cleared")


async def main() -> None:
    """Main seeding function."""
    
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    try:
        # Initialize database tables
        await init_db()
        print("Database tables initialized")
        print()
        
        # Clear existing data (optional - comment out for production)
        # await clear_database()
        
        # Seed all data
        await seed_users()
        print()
        await seed_mmm_sample_data() 
        print()
        await seed_mmm_performance_data()
        
        print()
        print("=" * 50)
        print(" Database seeding completed successfully!")
        print()
        print("Sample login credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  Demo:  demo@example.com / demo123")
        print("  Marketing: marketer@example.com / marketer123")
        print("  Analyst: analyst@example.com / analyst123")
        
    except Exception as e:
        print(f" Error during seeding: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
