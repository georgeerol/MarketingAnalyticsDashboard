"""
MMM (Media Mix Modeling) API routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.schemas.mmm import MMMModelInfo
from app.services.mmm_service import MMMModelError
from app.services.interfaces import MMMServiceProtocol
from app.api.deps import get_mmm_service, get_current_active_user_dep

router = APIRouter()


@router.get("/info", response_model=MMMModelInfo)
async def get_mmm_info(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Return MMM model metadata."""
    try:
        return mmm_service.get_model_info()
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/channels")
async def get_media_channels(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Return available media channels."""
    try:
        channels = mmm_service.get_channel_names()
        
        return {
            "channels": channels,
            "count": len(channels),
            "message": f"Found {len(channels)} media channels"
        }
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/contribution")
async def get_contribution_data(
    channel: Optional[str] = Query(None, description="Specific channel to filter by"),
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Return contribution data for channels."""
    try:
        return mmm_service.get_contribution_data(channel)
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/response-curves")
async def get_response_curves(
    channel: Optional[str] = Query(None, description="Specific channel to filter by"),
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Return response curves for channels."""
    try:
        return mmm_service.get_response_curves(channel)
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/channels/summary")
async def get_channel_summary(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Return per-channel summary metrics."""
    try:
        return mmm_service.get_channel_summary()
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
