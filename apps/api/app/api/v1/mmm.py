"""
MMM (Media Mix Modeling) API routes.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.schemas.mmm import (
    MMMStatus, MMMModelInfo, ContributionData, 
    ResponseCurveData, MMMChannelSummary
)
from app.services.mmm_service import MMMModelError
from app.services.interfaces import MMMServiceProtocol
from app.api.deps import get_mmm_service, get_current_active_user_dep

router = APIRouter()


@router.get("/status", response_model=MMMStatus)
async def get_mmm_status(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Check MMM model status"""
    return mmm_service.get_model_status()


@router.get("/info", response_model=MMMModelInfo)
async def get_mmm_info(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Get MMM model info"""
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
    """Get available media channels"""
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
    """Get channel contribution data"""
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
    """Get response curves for channels"""
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
    """Get channel performance summary"""
    try:
        return mmm_service.get_channel_summary()
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/explore")
async def explore_mmm_model(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Explore MMM model capabilities"""
    try:
        status = mmm_service.get_model_status()
        info = mmm_service.get_model_info()
        channels = mmm_service.get_channel_names()
        
        return {
            "status": status,
            "info": info,
            "channels": {
                "names": channels,
                "count": len(channels)
            },
            "capabilities": {
                "contribution_analysis": True,
                "response_curves": True,
                "channel_summary": True,
                "saturation_analysis": True,
                "efficiency_scoring": True
            }
        }
    except MMMModelError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/test")
async def test_mmm_model(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Test MMM model functionality"""
    try:
        test_results = {
            "model_status": "unknown",
            "channels_loaded": False,
            "contribution_data": False,
            "response_curves": False,
            "errors": []
        }
        
        # Test model status
        try:
            status = mmm_service.get_model_status()
            test_results["model_status"] = status.status
        except Exception as e:
            test_results["errors"].append(f"Status check failed: {str(e)}")
        
        # Test channel loading
        try:
            channels = mmm_service.get_channel_names()
            test_results["channels_loaded"] = len(channels) > 0
            test_results["channel_count"] = len(channels)
        except Exception as e:
            test_results["errors"].append(f"Channel loading failed: {str(e)}")
        
        # Test contribution data
        try:
            contribution = mmm_service.get_contribution_data()
            test_results["contribution_data"] = len(contribution.get("data", [])) > 0
        except Exception as e:
            test_results["errors"].append(f"Contribution data failed: {str(e)}")
        
        # Test response curves
        try:
            curves = mmm_service.get_response_curves()
            test_results["response_curves"] = len(curves.get("curves", {})) > 0
        except Exception as e:
            test_results["errors"].append(f"Response curves failed: {str(e)}")
        
        # Overall test result
        test_results["overall_status"] = "pass" if len(test_results["errors"]) == 0 else "fail"
        
        return test_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MMM test failed: {str(e)}"
        )


@router.get("/debug")
async def debug_mmm_model(
    current_user = Depends(get_current_active_user_dep),
    mmm_service: MMMServiceProtocol = Depends(get_mmm_service)
):
    """Debug MMM model parameters"""
    try:
        # Get debug information about model parameters
        model = mmm_service._load_model()
        debug_info = mmm_service._debug_model_parameters(model)
        
        return {
            "debug_status": "success",
            "model_debug": debug_info,
            "message": "Model parameter debugging completed"
        }
        
    except Exception as e:
        logger.error(f"MMM debugging failed: {e}")
        return {
            "debug_status": "failed",
            "error": str(e),
            "message": "MMM model debugging encountered errors"
        }
