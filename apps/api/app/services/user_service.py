"""
User service for user management business logic.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
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
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[User]:
        """Get list of users with pagination."""
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_users_count(self, active_only: bool = True) -> int:
        """Get total count of users."""
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.count()
    
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
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: ID of user to update
            user_data: Updated user data
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated user {user_id}")
            return user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database error updating user {user_id}: {e}")
            raise ValueError("Error updating user")
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user (soft delete).
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            True if user was deactivated, False if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        
        logger.info(f"Deactivated user {user_id}")
        return True
    
    def activate_user(self, user_id: int) -> bool:
        """
        Activate a user.
        
        Args:
            user_id: ID of user to activate
            
        Returns:
            True if user was activated, False if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        
        logger.info(f"Activated user {user_id}")
        return True
