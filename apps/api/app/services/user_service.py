"""
User service for user management business logic.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError(f"User with email {user_data.email} already exists")
        
        try:
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user instance
            db_user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                company=user_data.company,
                role="user",  # Default role
                is_active=True
            )
            
            # Save to database
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Created new user: {user_data.email}")
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database error creating user {user_data.email}: {e}")
            raise ValueError(f"User with email {user_data.email} already exists")
    
