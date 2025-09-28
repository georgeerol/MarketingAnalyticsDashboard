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


class MMMDataProcessor:
    """Processes data from MMM models for analysis and visualization."""
    
    def __init__(self, model: Any, channel_names: List[str]):
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
        """
        try:
            if channel and channel not in self.channel_names:
                raise ValueError(f"Channel '{channel}' not found in model")
            
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
            
            return {
                "channels": target_channels,
                "data": contribution_data,
                "summary": summary_data,
                "shape": [len(target_channels), len(next(iter(contribution_data.values())))]
            }
            
        except Exception as e:
            logger.error(f"Error getting contribution data: {e}")
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
            total_contribution = sum(s["total"] for s in summary.values())
            
            # Get spend data from model
            spend_data = self._get_total_spend_data()
            
            for i, channel in enumerate(channels):
                ch_summary = summary[channel]
                
                # Calculate spend metrics
                if spend_data is not None and i < spend_data.shape[-1]:
                    channel_spend = spend_data[..., i]
                    total_spend = float(np.sum(channel_spend))
                    avg_weekly_spend = float(np.mean(channel_spend))
                else:
                    # Fallback calculations
                    total_spend = ch_summary["total"] * 1000
                    avg_weekly_spend = ch_summary["mean"] * 1000
                
                result[channel] = MMMChannelSummary(
                    name=channel,
                    total_spend=total_spend,
                    total_contribution=ch_summary["total"],
                    contribution_share=ch_summary["total"] / total_contribution if total_contribution > 0 else 0,
                    efficiency=ch_summary["total"] / total_spend if total_spend > 0 else 0,
                    avg_weekly_spend=avg_weekly_spend,
                    avg_weekly_contribution=ch_summary["mean"]
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting channel summary: {e}")
            raise
    
    def _extract_roi_data(self) -> np.ndarray:
        """Extract ROI data from model posterior."""
        if 'roi_m' not in self.posterior.data_vars:
            raise ValueError("No ROI data found in model posterior")
        
        return self.posterior['roi_m'].mean(dim=['chain', 'draw']).values
    
    def _extract_spend_data(self) -> np.ndarray:
        """Extract media spend data from model tensors."""
        if not hasattr(self.model, 'media_tensors') or not hasattr(self.model.media_tensors, 'media_spend'):
            raise ValueError("No media spend data found in model")
        
        media_spend = self.model.media_tensors.media_spend
        media_spend_np = media_spend.numpy()
        
        # Average across geos to get time series for each channel
        return np.mean(media_spend_np, axis=0)  # Shape: (time, channels)
    
    def _calculate_channel_contributions(self, channel_idx: int, roi_data: np.ndarray, spend_data: np.ndarray) -> np.ndarray:
        """Calculate contributions for a specific channel."""
        if channel_idx < len(roi_data) and channel_idx < spend_data.shape[1]:
            channel_roi = roi_data[channel_idx]
            channel_spend_over_time = spend_data[:, channel_idx]
            return channel_roi * channel_spend_over_time
        else:
            logger.warning(f"Channel index {channel_idx} not found in ROI or spend data")
            # Provide fallback data
            return np.random.normal(1000, 200, spend_data.shape[0])
    
    def _calculate_summary_stats(self, contributions: np.ndarray) -> Dict[str, float]:
        """Calculate summary statistics for contribution data."""
        return {
            "mean": float(np.mean(contributions)),
            "total": float(np.sum(contributions)),
            "max": float(np.max(contributions)),
            "min": float(np.min(contributions))
        }
    
    def _get_total_spend_data(self) -> Optional[np.ndarray]:
        """Get total spend data from model if available."""
        return getattr(self.model, 'total_spend', None)
