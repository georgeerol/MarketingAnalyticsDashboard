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
    """Register a new user and return auth response."""
    try:
        user = user_service.create_user(user_data)
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        auth_response = auth_service.login(login_data)
        return auth_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User created but auto-login failed"
        )


@router.post("/login", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceProtocol = Depends(get_auth_service)
):
    """Login with username/password"""
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


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user = Depends(get_current_active_user_dep)
):
    """Return current authenticated user info."""
    return UserResponse.model_validate(current_user)


