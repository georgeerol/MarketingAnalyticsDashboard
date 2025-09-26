"""
MMM (Media Mix Modeling) routes for Google Meridian model data access.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from database import get_db
from auth_utils import get_current_active_user
from models import User
from mmm_utils import mmm_loader, check_mmm_file_exists

router = APIRouter(prefix="/mmm", tags=["mmm"])

@router.get("/status")
async def get_mmm_status(current_user: User = Depends(get_current_active_user)):
    """Get the status of the MMM model file and basic info."""
    try:
        file_exists = check_mmm_file_exists()
        
        if not file_exists:
            return {
                "status": "error",
                "message": "MMM model file not found",
                "file_exists": False,
                "model_path": str(mmm_loader.model_path)
            }
        
        # Get model info without fully loading it
        info = mmm_loader.get_model_info()
        
        return {
            "status": "success",
            "message": "MMM model file found and accessible",
            "file_exists": True,
            "model_info": info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking MMM status: {str(e)}")

@router.get("/info")
async def get_mmm_info(current_user: User = Depends(get_current_active_user)):
    """Get detailed information about the MMM model."""
    try:
        if not check_mmm_file_exists():
            raise HTTPException(status_code=404, detail="MMM model file not found")
        
        info = mmm_loader.get_model_info()
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MMM info: {str(e)}")

@router.get("/channels")
async def get_media_channels(current_user: User = Depends(get_current_active_user)):
    """Get the list of media channels from the MMM model."""
    try:
        if not check_mmm_file_exists():
            raise HTTPException(status_code=404, detail="MMM model file not found")
        
        channels = mmm_loader.get_media_channels()
        
        return {
            "channels": channels,
            "count": len(channels),
            "message": f"Found {len(channels)} media channels"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting media channels: {str(e)}")

@router.get("/contribution")
async def get_contribution_data(
    channel: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get media contribution data from the MMM model.
    
    Args:
        channel: Optional specific channel to filter by
    """
    try:
        if not check_mmm_file_exists():
            raise HTTPException(status_code=404, detail="MMM model file not found")
        
        contribution_df = mmm_loader.get_contribution_data()
        
        if contribution_df is None:
            raise HTTPException(status_code=404, detail="No contribution data found in MMM model")
        
        # Convert DataFrame to dict for JSON response
        if channel and channel in contribution_df.columns:
            # Return data for specific channel
            data = {
                "channel": channel,
                "data": contribution_df[channel].tolist(),
                "summary": {
                    "mean": float(contribution_df[channel].mean()),
                    "total": float(contribution_df[channel].sum()),
                    "max": float(contribution_df[channel].max()),
                    "min": float(contribution_df[channel].min())
                }
            }
        else:
            # Return all contribution data
            data = {
                "channels": list(contribution_df.columns),
                "data": contribution_df.to_dict('records'),
                "summary": {
                    col: {
                        "mean": float(contribution_df[col].mean()),
                        "total": float(contribution_df[col].sum()),
                        "max": float(contribution_df[col].max()),
                        "min": float(contribution_df[col].min())
                    }
                    for col in contribution_df.columns
                },
                "shape": contribution_df.shape
            }
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting contribution data: {str(e)}")

@router.get("/response-curves")
async def get_response_curves(
    channel: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get response curve data from the MMM model.
    
    Args:
        channel: Optional specific channel to get curves for
    """
    try:
        if not check_mmm_file_exists():
            raise HTTPException(status_code=404, detail="MMM model file not found")
        
        curves_data = mmm_loader.get_response_curves()
        
        if curves_data is None:
            raise HTTPException(status_code=404, detail="No response curve data found in MMM model")
        
        if channel and isinstance(curves_data, dict) and channel in curves_data:
            # Return curves for specific channel
            return {
                "channel": channel,
                "curves": curves_data[channel],
                "message": f"Response curves for {channel}"
            }
        else:
            # Return all response curves
            return {
                "curves": curves_data,
                "channels": list(curves_data.keys()) if isinstance(curves_data, dict) else "Unknown structure",
                "message": "All response curves data"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response curves: {str(e)}")

@router.get("/explore")
async def explore_mmm_model(current_user: User = Depends(get_current_active_user)):
    """Explore the MMM model structure to understand available data."""
    try:
        if not check_mmm_file_exists():
            raise HTTPException(status_code=404, detail="MMM model file not found")
        
        # Load the model to explore its structure
        model_data = mmm_loader.load_model()
        
        exploration = {
            "data_type": type(model_data).__name__,
            "structure": {}
        }
        
        if isinstance(model_data, dict):
            exploration["structure"] = {
                key: {
                    "type": type(value).__name__,
                    "shape": getattr(value, 'shape', None) if hasattr(value, 'shape') else None,
                    "size": len(value) if hasattr(value, '__len__') else None,
                    "keys": list(value.keys()) if isinstance(value, dict) else None,
                    "columns": list(value.columns) if hasattr(value, 'columns') else None,
                    "sample": str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                }
                for key, value in model_data.items()
            }
        else:
            exploration["structure"] = {
                "raw_data": {
                    "type": type(model_data).__name__,
                    "shape": getattr(model_data, 'shape', None) if hasattr(model_data, 'shape') else None,
                    "sample": str(model_data)[:500] + "..." if len(str(model_data)) > 500 else str(model_data)
                }
            }
        
        return exploration
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exploring MMM model: {str(e)}")

@router.get("/test")
async def test_mmm_loading(current_user: User = Depends(get_current_active_user)):
    """Test endpoint to validate MMM model loading and basic functionality."""
    try:
        results = {
            "file_check": check_mmm_file_exists(),
            "model_info": None,
            "channels": None,
            "contribution_available": False,
            "response_curves_available": False,
            "errors": []
        }
        
        if not results["file_check"]:
            results["errors"].append("MMM model file not found")
            return results
        
        # Test model info
        try:
            results["model_info"] = mmm_loader.get_model_info()
        except Exception as e:
            results["errors"].append(f"Model info error: {str(e)}")
        
        # Test channels
        try:
            channels = mmm_loader.get_media_channels()
            results["channels"] = {
                "list": channels,
                "count": len(channels)
            }
        except Exception as e:
            results["errors"].append(f"Channels error: {str(e)}")
        
        # Test contribution data
        try:
            contribution_df = mmm_loader.get_contribution_data()
            results["contribution_available"] = contribution_df is not None
            if contribution_df is not None:
                results["contribution_shape"] = contribution_df.shape
        except Exception as e:
            results["errors"].append(f"Contribution data error: {str(e)}")
        
        # Test response curves
        try:
            curves = mmm_loader.get_response_curves()
            results["response_curves_available"] = curves is not None
            if curves is not None:
                results["response_curves_keys"] = list(curves.keys()) if isinstance(curves, dict) else "Not a dict"
        except Exception as e:
            results["errors"].append(f"Response curves error: {str(e)}")
        
        results["status"] = "success" if len(results["errors"]) == 0 else "partial"
        results["message"] = "MMM model testing completed"
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing MMM model: {str(e)}")
