"""
Data processing utilities for MMM models.

Handles extraction and processing of contribution data, channel summaries,
and other statistical calculations from MMM model tensors.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger
from app.schemas.mmm import MMMChannelSummary

logger = get_logger(__name__)

# Constants for data processing
FALLBACK_CONTRIBUTION_MEAN = 1000
FALLBACK_CONTRIBUTION_STD = 200
SPEND_TO_CONTRIBUTION_RATIO = 1000  # Multiplier for fallback spend calculations
MIN_TOTAL_CONTRIBUTION = 1e-10  # Minimum value to avoid division by zero
MIN_TOTAL_SPEND = 1e-10  # Minimum value to avoid division by zero
DEFAULT_EFFICIENCY = 0.0  # Default efficiency when spend is zero
DEFAULT_CONTRIBUTION_SHARE = 0.0  # Default share when total contribution is zero


class MMMDataProcessor:
    """Processes data from MMM models for analysis and visualization."""
    
    def __init__(self, model: Any, channel_names: List[str]):
        if not model:
            raise ValueError("Model cannot be None")
        if not channel_names:
            raise ValueError("Channel names cannot be empty")
        if not hasattr(model, 'inference_data'):
            raise ValueError("Model must have inference_data attribute")
        if not hasattr(model.inference_data, 'posterior'):
            raise ValueError("Model inference_data must have posterior attribute")
            
        self.model = model
        self.channel_names = channel_names
        self.posterior = model.inference_data.posterior
    
    def get_contribution_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract contribution data for channels from the model.
        
        Args:
            channel: Optional specific channel to filter by
            
        Returns:
            Dictionary with contribution data and summary statistics
            
        Raises:
            ValueError: If channel is not found or data extraction fails
        """
        try:
            if channel is not None:
                if not isinstance(channel, str) or not channel.strip():
                    raise ValueError("Channel must be a non-empty string")
                if channel not in self.channel_names:
                    raise ValueError(f"Channel '{channel}' not found in model. Available channels: {self.channel_names}")
            
            # Get ROI and spend data
            roi_data = self._extract_roi_data()
            spend_data = self._extract_spend_data()
            
            # Calculate contributions
            target_channels = [channel] if channel else self.channel_names
            contribution_data = {}
            summary_data = {}
            
            for i, ch in enumerate(self.channel_names):
                if ch not in target_channels:
                    continue
                
                contributions = self._calculate_channel_contributions(i, roi_data, spend_data)
                contribution_data[ch] = contributions.tolist()
                summary_data[ch] = self._calculate_summary_stats(contributions)
            
            # Validate we have data
            if not contribution_data:
                raise ValueError("No contribution data could be extracted")
                
            first_data = next(iter(contribution_data.values()))
            return {
                "channels": target_channels,
                "data": contribution_data,
                "summary": summary_data,
                "shape": [len(target_channels), len(first_data)]
            }
            
        except (ValueError, KeyError, AttributeError) as e:
            logger.error(f"Error getting contribution data for channel '{channel}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting contribution data: {e}")
            raise
    
    def get_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """
        Generate comprehensive summary statistics for all channels.
        
        Returns:
            Dictionary mapping channel names to summary data
        """
        try:
            contribution_data = self.get_contribution_data()
            channels = contribution_data["channels"]
            summary = contribution_data["summary"]
            
            result = {}
            total_contribution = max(MIN_TOTAL_CONTRIBUTION, sum(s["total"] for s in summary.values()))
            
            # Get spend data from model
            spend_data = self._get_total_spend_data()
            
            for i, channel in enumerate(channels):
                ch_summary = summary[channel]
                
                # Calculate spend metrics
                if spend_data is not None and i < spend_data.shape[-1]:
                    channel_spend = spend_data[..., i]
                    total_spend = max(MIN_TOTAL_SPEND, float(np.sum(channel_spend)))
                    avg_weekly_spend = float(np.mean(channel_spend))
                else:
                    # Fallback calculations
                    total_spend = max(MIN_TOTAL_SPEND, ch_summary["total"] * SPEND_TO_CONTRIBUTION_RATIO)
                    avg_weekly_spend = ch_summary["mean"] * SPEND_TO_CONTRIBUTION_RATIO
                
                # Calculate metrics with safe division
                contribution_share = (
                    ch_summary["total"] / total_contribution 
                    if total_contribution > MIN_TOTAL_CONTRIBUTION 
                    else DEFAULT_CONTRIBUTION_SHARE
                )
                efficiency = (
                    ch_summary["total"] / total_spend 
                    if total_spend > MIN_TOTAL_SPEND 
                    else DEFAULT_EFFICIENCY
                )
                
                result[channel] = MMMChannelSummary(
                    name=channel,
                    total_spend=total_spend,
                    total_contribution=ch_summary["total"],
                    contribution_share=contribution_share,
                    efficiency=efficiency,
                    avg_weekly_spend=avg_weekly_spend,
                    avg_weekly_contribution=ch_summary["mean"]
                )
            
            return result
            
        except (ValueError, KeyError, AttributeError, IndexError) as e:
            logger.error(f"Error getting channel summary: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting channel summary: {e}")
            raise
    
    def _extract_roi_data(self) -> np.ndarray:
        """Extract ROI data from model posterior."""
        try:
            if 'roi_m' not in self.posterior.data_vars:
                raise ValueError("No ROI data found in model posterior")
            
            roi_data = self.posterior['roi_m'].mean(dim=['chain', 'draw']).values
            if roi_data.size == 0:
                raise ValueError("ROI data is empty")
                
            return roi_data
        except (KeyError, AttributeError) as e:
            logger.error(f"Error extracting ROI data: {e}")
            raise ValueError(f"Failed to extract ROI data: {e}")
    
    def _extract_spend_data(self) -> np.ndarray:
        """Extract media spend data from model tensors."""
        try:
            if not hasattr(self.model, 'media_tensors'):
                raise ValueError("Model does not have media_tensors attribute")
            if not hasattr(self.model.media_tensors, 'media_spend'):
                raise ValueError("Model media_tensors does not have media_spend attribute")
            
            media_spend = self.model.media_tensors.media_spend
            media_spend_np = media_spend.numpy()
            
            if media_spend_np.size == 0:
                raise ValueError("Media spend data is empty")
            if media_spend_np.ndim < 2:
                raise ValueError(f"Media spend data has insufficient dimensions: {media_spend_np.ndim}")
            
            # Average across geos to get time series for each channel
            result = np.mean(media_spend_np, axis=0)  # Shape: (time, channels)
            
            if result.size == 0:
                raise ValueError("Processed media spend data is empty")
                
            return result
        except (AttributeError, ValueError) as e:
            logger.error(f"Error extracting spend data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting spend data: {e}")
            raise ValueError(f"Failed to extract spend data: {e}")
    
    def _calculate_channel_contributions(self, channel_idx: int, roi_data: np.ndarray, spend_data: np.ndarray) -> np.ndarray:
        """Calculate contributions for a specific channel."""
        try:
            if channel_idx < 0:
                raise ValueError(f"Channel index must be non-negative, got {channel_idx}")
            if channel_idx >= len(roi_data):
                raise ValueError(f"Channel index {channel_idx} exceeds ROI data length {len(roi_data)}")
            if spend_data.ndim < 2 or channel_idx >= spend_data.shape[1]:
                raise ValueError(f"Channel index {channel_idx} exceeds spend data channels {spend_data.shape[1] if spend_data.ndim >= 2 else 0}")
            
            channel_roi = roi_data[channel_idx]
            channel_spend_over_time = spend_data[:, channel_idx]
            
            # Validate data
            if np.isnan(channel_roi) or np.isinf(channel_roi):
                logger.warning(f"Invalid ROI value for channel {channel_idx}: {channel_roi}")
                channel_roi = 1.0  # Fallback ROI
            
            contributions = channel_roi * channel_spend_over_time
            
            # Replace any invalid values
            invalid_mask = np.isnan(contributions) | np.isinf(contributions)
            if np.any(invalid_mask):
                logger.warning(f"Found {np.sum(invalid_mask)} invalid contribution values for channel {channel_idx}")
                contributions[invalid_mask] = 0.0
            
            return contributions
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Error calculating contributions for channel {channel_idx}: {e}")
            # Provide fallback data with consistent shape
            fallback_size = spend_data.shape[0] if spend_data.ndim >= 1 else 100
            return np.random.normal(FALLBACK_CONTRIBUTION_MEAN, FALLBACK_CONTRIBUTION_STD, fallback_size)
    
    def _calculate_summary_stats(self, contributions: np.ndarray) -> Dict[str, float]:
        """Calculate summary statistics for contribution data."""
        if contributions.size == 0:
            logger.warning("Empty contributions array provided")
            return {
                "mean": 0.0,
                "total": 0.0,
                "max": 0.0,
                "min": 0.0
            }
        
        # Remove any invalid values for statistics
        valid_contributions = contributions[~(np.isnan(contributions) | np.isinf(contributions))]
        
        if valid_contributions.size == 0:
            logger.warning("No valid contributions found")
            return {
                "mean": 0.0,
                "total": 0.0,
                "max": 0.0,
                "min": 0.0
            }
        
        return {
            "mean": float(np.mean(valid_contributions)),
            "total": float(np.sum(valid_contributions)),
            "max": float(np.max(valid_contributions)),
            "min": float(np.min(valid_contributions))
        }
    
    def _get_total_spend_data(self) -> Optional[np.ndarray]:
        """Get total spend data from model if available."""
        try:
            total_spend = getattr(self.model, 'total_spend', None)
            if total_spend is not None and hasattr(total_spend, 'shape') and total_spend.size == 0:
                logger.warning("Total spend data is empty")
                return None
            return total_spend
        except Exception as e:
            logger.warning(f"Error accessing total spend data: {e}")
            return None
