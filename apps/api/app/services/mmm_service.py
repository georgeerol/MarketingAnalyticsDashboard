"""
MMM (Media Mix Modeling) service for handling Google Meridian model operations.
"""

import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.mmm import (
    MMMStatus, MMMModelInfo, ContributionData, 
    ResponseCurveData, MMMChannelSummary
)

settings = get_settings()
logger = get_logger(__name__)


class MMMModelError(Exception):
    """Exception raised for MMM model related errors."""
    pass


class MMMService:
    """Service class for MMM model operations and data processing."""
    
    def __init__(self):
        self.model_path = settings.MMM_MODEL_FULL_PATH
        self._model_data = None
        self._is_loaded = False
        self._use_mock_data = settings.USE_MOCK_DATA
    
    def get_model_status(self) -> MMMStatus:
        """
        Get the status of the MMM model.
        
        Returns:
            MMMStatus with current model status information
        """
        try:
            file_exists = self.model_path.exists()
            
            if not file_exists and not self._use_mock_data:
                return MMMStatus(
                    status="error",
                    message="MMM model file not found",
                    file_exists=False,
                    model_info=None
                )
            
            # Try to get basic model info
            model_info = self._get_basic_model_info()
            
            return MMMStatus(
                status="success",
                message="MMM model available",
                file_exists=file_exists or self._use_mock_data,
                model_info=model_info
            )
            
        except Exception as e:
            logger.error(f"Error checking MMM status: {e}")
            return MMMStatus(
                status="error",
                message=f"Error checking MMM status: {str(e)}",
                file_exists=False,
                model_info=None
            )
    
    def get_model_info(self) -> MMMModelInfo:
        """
        Get detailed information about the MMM model.
        
        Returns:
            MMMModelInfo with model details
            
        Raises:
            MMMModelError: If model cannot be loaded
        """
        try:
            model = self._load_model()
            
            if self._use_mock_data or not hasattr(model, 'trace'):
                # Return mock model info
                return MMMModelInfo(
                    model_type="Google Meridian (Mock)",
                    version="1.0.0-mock",
                    training_period="2022-01-01 to 2024-01-01",
                    channels=self._get_channel_names(),
                    data_frequency="weekly",
                    total_weeks=104,
                    data_source="mock_data"
                )
            
            # Extract real model info
            channels = self._get_channel_names()
            
            return MMMModelInfo(
                model_type="Google Meridian",
                version="1.0.0",
                training_period="Model training period",
                channels=channels,
                data_frequency="weekly",
                total_weeks=len(self._get_contribution_data_raw()),
                data_source="real_model"
            )
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise MMMModelError(f"Failed to get model info: {str(e)}")
    
    def get_channel_names(self) -> List[str]:
        """
        Get list of channel names from the model.
        
        Returns:
            List of channel names
        """
        return self._get_channel_names()
    
    def get_contribution_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Get contribution data for channels.
        
        Args:
            channel: Optional specific channel name to filter by
            
        Returns:
            Dictionary with contribution data
        """
        try:
            model = self._load_model()
            channels = self._get_channel_names()
            contribution_data = self._get_contribution_data_raw()
            
            if channel and channel not in channels:
                raise MMMModelError(f"Channel '{channel}' not found in model")
            
            # Process contribution data
            result = {
                "channels": channels,
                "data": [],
                "summary": {},
                "shape": contribution_data.shape if hasattr(contribution_data, 'shape') else [0, 0]
            }
            
            # Convert to list format for API response
            if isinstance(contribution_data, (pd.DataFrame, np.ndarray)):
                if channel:
                    # Filter for specific channel
                    if channel in channels:
                        channel_idx = channels.index(channel)
                        if isinstance(contribution_data, pd.DataFrame):
                            channel_data = contribution_data.iloc[:, channel_idx].tolist()
                        else:
                            channel_data = contribution_data[:, channel_idx].tolist()
                        
                        result["data"] = [{channel: val} for val in channel_data]
                        result["summary"][channel] = {
                            "mean": float(np.mean(channel_data)),
                            "total": float(np.sum(channel_data)),
                            "max": float(np.max(channel_data)),
                            "min": float(np.min(channel_data))
                        }
                else:
                    # All channels
                    if isinstance(contribution_data, pd.DataFrame):
                        data_dict = contribution_data.to_dict('records')
                    else:
                        data_dict = [
                            {channels[i]: float(contribution_data[row, i]) 
                             for i in range(len(channels))}
                            for row in range(contribution_data.shape[0])
                        ]
                    
                    result["data"] = data_dict
                    
                    # Calculate summary statistics
                    for i, ch in enumerate(channels):
                        if isinstance(contribution_data, pd.DataFrame):
                            ch_data = contribution_data.iloc[:, i]
                        else:
                            ch_data = contribution_data[:, i]
                        
                        result["summary"][ch] = {
                            "mean": float(np.mean(ch_data)),
                            "total": float(np.sum(ch_data)),
                            "max": float(np.max(ch_data)),
                            "min": float(np.min(ch_data))
                        }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting contribution data: {e}")
            raise MMMModelError(f"Failed to get contribution data: {str(e)}")
    
    def get_response_curves(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Get response curve data for channels.
        
        Args:
            channel: Optional specific channel name to filter by
            
        Returns:
            Dictionary with response curve data
        """
        try:
            model = self._load_model()
            channels = self._get_channel_names()
            
            if channel and channel not in channels:
                raise MMMModelError(f"Channel '{channel}' not found in model")
            
            curves = {}
            target_channels = [channel] if channel else channels
            
            for ch in target_channels:
                curve_data = self._generate_response_curve(ch)
                curves[ch] = curve_data
            
            return {"curves": curves}
            
        except Exception as e:
            logger.error(f"Error getting response curves: {e}")
            raise MMMModelError(f"Failed to get response curves: {str(e)}")
    
    def get_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """
        Get summary statistics for all channels.
        
        Returns:
            Dictionary mapping channel names to summary data
        """
        try:
            contribution_data = self.get_contribution_data()
            channels = contribution_data["channels"]
            summary = contribution_data["summary"]
            
            result = {}
            total_contribution = sum(s["total"] for s in summary.values())
            
            for channel in channels:
                ch_summary = summary[channel]
                
                result[channel] = MMMChannelSummary(
                    name=channel,
                    total_spend=ch_summary["total"] * 1.2,  # Mock spend calculation
                    total_contribution=ch_summary["total"],
                    contribution_share=ch_summary["total"] / total_contribution if total_contribution > 0 else 0,
                    efficiency=ch_summary["mean"] / (ch_summary["total"] * 1.2) if ch_summary["total"] > 0 else 0,
                    avg_weekly_spend=ch_summary["mean"] * 1.2,
                    avg_weekly_contribution=ch_summary["mean"]
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting channel summary: {e}")
            raise MMMModelError(f"Failed to get channel summary: {str(e)}")
    
    def _load_model(self) -> Any:
        """Load the MMM model with fallback to mock data."""
        if self._is_loaded and self._model_data is not None:
            return self._model_data
        
        if self._use_mock_data:
            logger.info("Using mock MMM data")
            self._model_data = self._generate_mock_model()
            self._is_loaded = True
            return self._model_data
        
        if not self.model_path.exists():
            logger.warning(f"MMM model file not found at {self.model_path}, using mock data")
            self._model_data = self._generate_mock_model()
            self._is_loaded = True
            return self._model_data
        
        try:
            # Try to load with Google Meridian
            from meridian.model.model import load_mmm
            logger.info(f"Loading real MMM model from {self.model_path}")
            self._model_data = load_mmm(str(self.model_path))
            self._is_loaded = True
            logger.info("Successfully loaded real MMM model")
            return self._model_data
            
        except ImportError:
            logger.warning("Google Meridian package not available, using mock data")
            self._model_data = self._generate_mock_model()
            self._is_loaded = True
            return self._model_data
        
        except Exception as e:
            logger.error(f"Error loading MMM model: {e}, using mock data")
            self._model_data = self._generate_mock_model()
            self._is_loaded = True
            return self._model_data
    
    def _get_channel_names(self) -> List[str]:
        """Get channel names from the model."""
        # This would be extracted from the real model
        # For now, return mock channel names
        return ["Google_Search", "Google_Display", "Facebook", "Instagram", "YouTube"]
    
    def _get_contribution_data_raw(self) -> Any:
        """Get raw contribution data from the model."""
        # This would extract real contribution data from the model
        # For now, generate mock data
        channels = self._get_channel_names()
        weeks = 104
        
        # Generate realistic contribution data
        np.random.seed(42)  # For reproducible results
        data = np.random.exponential(scale=1000, size=(weeks, len(channels)))
        
        return pd.DataFrame(data, columns=channels)
    
    def _generate_response_curve(self, channel: str) -> Dict[str, Any]:
        """Generate response curve data for a channel."""
        # This would use real model parameters
        # For now, generate mock curve
        max_spend = 50000
        spend_points = np.linspace(0, max_spend, 50)
        
        # Hill saturation curve parameters (mock)
        alpha = np.random.uniform(0.5, 2.0)
        ec = np.random.uniform(10000, 30000)
        
        # Calculate response using Hill saturation
        response_points = (spend_points ** alpha) / (ec ** alpha + spend_points ** alpha) * max_spend * 0.8
        
        return {
            "spend": spend_points.tolist(),
            "response": response_points.tolist(),
            "saturation_point": float(ec),
            "efficiency": float(alpha),
            "adstock_rate": np.random.uniform(0.1, 0.9)
        }
    
    def _generate_mock_model(self) -> Dict[str, Any]:
        """Generate mock model data."""
        return {
            "type": "mock",
            "channels": self._get_channel_names(),
            "data": self._get_contribution_data_raw()
        }
    
    def _get_basic_model_info(self) -> Dict[str, Any]:
        """Get basic model information without full loading."""
        return {
            "file_path": str(self.model_path),
            "file_exists": self.model_path.exists(),
            "file_size": self.model_path.stat().st_size if self.model_path.exists() else 0,
            "use_mock_data": self._use_mock_data
        }
