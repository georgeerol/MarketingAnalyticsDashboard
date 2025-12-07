"""
User service for user management business logic.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.core.logging import get_logger

logger = get_logger(__name__)

# User service constants
DEFAULT_USER_ROLE = "user"
DEFAULT_USER_STATUS = True  # Active by default
MAX_USERS_PER_PAGE = 100
DEFAULT_PAGE_SIZE = 20

# Valid user roles
VALID_USER_ROLES = [
    "user",
    "admin",
    "analyst",
    "viewer"
]

# User validation constants
MIN_PASSWORD_LENGTH = 8
MAX_EMAIL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_COMPANY_LENGTH = 100


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User instance if found, None otherwise
            
        Raises:
            ValueError: If user_id is invalid
            SQLAlchemyError: If database error occurs
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"Invalid user ID: {user_id}. Must be a positive integer.")
        
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                logger.debug(f"Found user with ID {user_id}: {user.email}")
            else:
                logger.debug(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving user {user_id}: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User instance if found, None otherwise
            
        Raises:
            ValueError: If email is invalid
            SQLAlchemyError: If database error occurs
        """
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")
        
        email = email.strip().lower()
        if not email or len(email) > MAX_EMAIL_LENGTH:
            raise ValueError(f"Invalid email length. Must be 1-{MAX_EMAIL_LENGTH} characters.")
        
        # Basic email format validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError(f"Invalid email format: {email}")
        
        try:
            user = self.db.query(User).filter(func.lower(User.email) == email).first()
            if user:
                logger.debug(f"Found user with email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving user by email {email}: {e}")
            raise
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If validation fails or email already exists
            SQLAlchemyError: If database error occurs
        """
        if not user_data:
            raise ValueError("User data cannot be None")
        
        # Validate user data
        self._validate_user_data(user_data)
        
        # Normalize email
        normalized_email = user_data.email.strip().lower()
        
        # Check if user already exists
        if self.get_user_by_email(normalized_email):
            raise ValueError(f"User with email {normalized_email} already exists")
        
        try:
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user instance
            db_user = User(
                email=normalized_email,
                hashed_password=hashed_password,
                full_name=user_data.full_name.strip() if user_data.full_name else None,
                company=user_data.company.strip() if user_data.company else None,
                role=DEFAULT_USER_ROLE,
                is_active=DEFAULT_USER_STATUS
            )
            
            # Save to database
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Created new user: {normalized_email} (ID: {db_user.id})")
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating user {normalized_email}: {e}")
            raise ValueError(f"User with email {normalized_email} already exists")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating user {normalized_email}: {e}")
            raise
    
    def _validate_user_data(self, user_data: UserCreate) -> None:
        """
        Validate user creation data.
        
        Args:
            user_data: User data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate email
        if not user_data.email or not user_data.email.strip():
            raise ValueError("Email is required")
        
        email = user_data.email.strip()
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValueError(f"Email too long. Maximum {MAX_EMAIL_LENGTH} characters.")
        
        # Basic email format validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError(f"Invalid email format: {email}")
        
        # Validate password
        if not user_data.password:
            raise ValueError("Password is required")
        if len(user_data.password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password too short. Minimum {MIN_PASSWORD_LENGTH} characters.")
        
        # Validate optional fields
        if user_data.full_name and len(user_data.full_name.strip()) > MAX_NAME_LENGTH:
            raise ValueError(f"Full name too long. Maximum {MAX_NAME_LENGTH} characters.")
        
        if user_data.company and len(user_data.company.strip()) > MAX_COMPANY_LENGTH:
            raise ValueError(f"Company name too long. Maximum {MAX_COMPANY_LENGTH} characters.")
