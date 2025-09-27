"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import UserLogin, AuthResponse, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthenticationError
from app.services.interfaces import UserServiceProtocol, AuthServiceProtocol
from app.api.deps import get_auth_service, get_user_service, get_current_active_user_dep

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserServiceProtocol = Depends(get_user_service),
    auth_service: AuthServiceProtocol = Depends(get_auth_service)
):
    """
    Register a new user and automatically log them in.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters)
    - **full_name**: User's full name
    - **company**: Optional company name
    
    Returns access token and user information for immediate login.
    """
    try:
        # Create the user
        user = user_service.create_user(user_data)
        
        # Automatically log in the newly created user
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        auth_response = auth_service.login(login_data)
        
        return auth_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthenticationError as e:
        # This shouldn't happen since we just created the user, but handle it gracefully
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User created but login failed. Please try logging in manually."
        )


@router.post("/login", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceProtocol = Depends(get_auth_service)
):
    """
    OAuth2 compatible login endpoint (for form-based authentication).
    
    Uses OAuth2PasswordRequestForm which expects:
    - **username**: User's email address
    - **password**: User's password
    """
    try:
        login_data = UserLogin(email=form_data.username, password=form_data.password)
        auth_response = auth_service.login(login_data)
        
        return Token(
            access_token=auth_response.access_token,
            token_type=auth_response.token_type
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login-json", response_model=AuthResponse)
async def login_json(
    login_data: UserLogin,
    auth_service: AuthServiceProtocol = Depends(get_auth_service)
):
    """
    JSON-based login endpoint (returns user data along with token).
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and user information.
    """
    try:
        return auth_service.login(login_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user = Depends(get_current_active_user_dep)
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user = Depends(get_current_active_user_dep),
    auth_service: AuthServiceProtocol = Depends(get_auth_service)
):
    """
    Refresh access token for current user.
    
    Requires valid JWT token in Authorization header.
    Returns new access token with extended expiration.
    """
    new_token = auth_service.refresh_token(current_user)
    return Token(access_token=new_token, token_type="bearer")
