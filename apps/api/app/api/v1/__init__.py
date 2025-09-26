"""
API v1 routes.
"""

from fastapi import APIRouter

from app.api.v1 import auth, mmm, users

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(mmm.router, prefix="/mmm", tags=["mmm"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
