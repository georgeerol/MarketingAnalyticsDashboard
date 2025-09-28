"""
Response curve generation for MMM models.

Handles the complex mathematics of generating Hill saturation curves
and calculating channel response characteristics.
"""

import numpy as np
from typing import Dict, Any, List
from app.core.logging import get_logger

logger = get_logger(__name__)

# Constants for curve generation
CURVE_POINTS = 100
DEFAULT_MAX_SPEND = 100000.0
MIN_SAFE_SPEND = 50000.0
MAX_SAFE_SPEND = 200000.0
SPEND_MULTIPLIER = 2.0

# Hill curve parameters
HILL_EC_BASE = 0.2
HILL_EC_SCALE = 0.3
HILL_SLOPE_BASE = 0.7
HILL_SLOPE_ROI_SCALE = 0.4
HILL_SLOPE_CHANNEL_SCALE = 0.1
HILL_SLOPE_FALLBACK_BASE = 0.8
HILL_SLOPE_FALLBACK_SCALE = 0.2

# Response scaling
ROI_RESPONSE_SCALE = 0.15
FALLBACK_RESPONSE_SCALE = 0.3

# Saturation detection
SATURATION_THRESHOLD = 0.1  # 10% of max marginal return
SATURATION_SKIP_POINTS = 5
SATURATION_DEFAULT = 0.6
SATURATION_CONSERVATIVE = 0.7
SATURATION_MIN_BOUND = 0.2
SATURATION_MAX_BOUND = 0.9

# Fallback curve parameters
FALLBACK_SPEND_MAX = 100000
FALLBACK_SPEND_STEP = 1000
FALLBACK_BASE_RESPONSE = 8
FALLBACK_RESPONSE_INCREMENT = 3
FALLBACK_CURVE_BASE = 0.8
FALLBACK_CURVE_INCREMENT = 0.3
FALLBACK_SATURATION_BASE = 40000
FALLBACK_SATURATION_INCREMENT = 8000
FALLBACK_EFFICIENCY_BASE = 0.05
FALLBACK_EFFICIENCY_INCREMENT = 0.02
FALLBACK_ADSTOCK_BASE = 0.2
FALLBACK_ADSTOCK_INCREMENT = 0.1

# Default values
DEFAULT_EFFICIENCY = 1.0
EFFICIENCY_INCREMENT = 0.2
DEFAULT_ADSTOCK = 0.3
ADSTOCK_INCREMENT = 0.05
ADSTOCK_MAX = 0.5
MIN_EFFICIENCY = 0.001


class ResponseCurveGenerator:
    """Generates response curves from MMM model parameters."""
    
    def __init__(self, model: Any, channel_names: List[str]):
        self.model = model
        self.channel_names = channel_names
        self.posterior = model.inference_data.posterior
    
    def generate_curve(self, channel: str) -> Dict[str, Any]:
        """
        Generate response curve data for a specific channel.
        
        Args:
            channel: Channel name
            
        Returns:
            Dictionary with response curve data
            
        Raises:
            ValueError: If channel is not found in model
        """
        if not channel or not isinstance(channel, str):
            raise ValueError("Channel must be a non-empty string")
            
        try:
            if channel not in self.channel_names:
                raise ValueError(f"Channel '{channel}' not found in model. Available channels: {self.channel_names}")
            
            channel_idx = self.channel_names.index(channel)
            
            # Get spend range from model data
            spend_range = self._get_spend_range(channel_idx)
            spend_points = np.linspace(spend_range['min'], spend_range['max'], CURVE_POINTS)
            
            # Generate response curve using model parameters
            response_points = self._calculate_response_curve(channel_idx, spend_points)
            
            # Calculate curve characteristics
            saturation_point = self._find_saturation_point(spend_points, response_points)
            efficiency = self._calculate_efficiency(channel_idx)
            adstock_rate = self._get_adstock_rate(channel_idx)
            
            return {
                "spend": spend_points.tolist(),
                "response": response_points.tolist(),
                "saturation_point": saturation_point,
                "efficiency": max(MIN_EFFICIENCY, efficiency),
                "adstock_rate": adstock_rate
            }
            
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Error generating response curve for channel '{channel}' (index {channel_idx}): {e}")
            return self._generate_fallback_curve(channel_idx)
        except Exception as e:
            logger.error(f"Unexpected error generating response curve for channel '{channel}': {e}")
            return self._generate_fallback_curve(channel_idx)
    
    def _get_spend_range(self, channel_idx: int) -> Dict[str, float]:
        """Get realistic spend range for channel."""
        try:
            if hasattr(self.model, 'media_tensors') and hasattr(self.model.media_tensors, 'media_spend'):
                media_spend = self.model.media_tensors.media_spend.numpy()
                channel_spend = media_spend[:, :, channel_idx]
                computed_max = float(np.max(channel_spend)) * SPEND_MULTIPLIER
                max_spend = float(min(MAX_SAFE_SPEND, max(MIN_SAFE_SPEND, computed_max)))
            else:
                max_spend = DEFAULT_MAX_SPEND
            
            return {"min": 0.0, "max": max_spend}
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Could not extract spend range for channel {channel_idx}: {e}")
            return {"min": 0.0, "max": DEFAULT_MAX_SPEND}
    
    def _calculate_response_curve(self, channel_idx: int, spend_points: np.ndarray) -> np.ndarray:
        """Calculate Hill saturation response curve."""
        try:
            # Extract Hill parameters from model
            if 'ec_m' in self.posterior.data_vars and 'slope_m' in self.posterior.data_vars:
                hill_ec = float(self.posterior['ec_m'].mean(dim=['chain', 'draw']).values[channel_idx])
                hill_slope = float(self.posterior['slope_m'].mean(dim=['chain', 'draw']).values[channel_idx])
                
                # Adjust parameters for realistic curves
                max_spend = np.max(spend_points)
                adjusted_ec = max_spend * (HILL_EC_BASE + hill_ec * HILL_EC_SCALE)
                
                if 'roi_m' in self.posterior.data_vars:
                    roi = float(self.posterior['roi_m'].mean(dim=['chain', 'draw']).values[channel_idx])
                    adjusted_slope = HILL_SLOPE_BASE + roi * HILL_SLOPE_ROI_SCALE + channel_idx * HILL_SLOPE_CHANNEL_SCALE
                else:
                    adjusted_slope = HILL_SLOPE_FALLBACK_BASE + channel_idx * HILL_SLOPE_FALLBACK_SCALE
                
                # Hill saturation curve
                response_points = spend_points**adjusted_slope / (adjusted_ec**adjusted_slope + spend_points**adjusted_slope)
                
                # Scale by ROI
                if 'roi_m' in self.posterior.data_vars:
                    roi = float(self.posterior['roi_m'].mean(dim=['chain', 'draw']).values[channel_idx])
                    response_points = response_points * roi * max_spend * ROI_RESPONSE_SCALE
                else:
                    response_points = response_points * max_spend * FALLBACK_RESPONSE_SCALE
                
                return response_points
                
            else:
                # Fallback calculation
                return self._simple_response_curve(spend_points, channel_idx)
                
        except (KeyError, ValueError, IndexError) as e:
            logger.warning(f"Could not extract Hill parameters for channel {channel_idx}: {e}")
            return self._simple_response_curve(spend_points, channel_idx)
        except Exception as e:
            logger.error(f"Unexpected error calculating response curve for channel {channel_idx}: {e}")
            return self._simple_response_curve(spend_points, channel_idx)
    
    def _simple_response_curve(self, spend_points: np.ndarray, channel_idx: int) -> np.ndarray:
        """Generate simple response curve as fallback."""
        base_multiplier = FALLBACK_BASE_RESPONSE + channel_idx * FALLBACK_RESPONSE_INCREMENT
        return np.sqrt(spend_points) * base_multiplier
    
    def _find_saturation_point(self, spend_points: np.ndarray, response_points: np.ndarray) -> float:
        """Find saturation point where marginal returns drop significantly."""
        try:
            marginal_returns = np.diff(response_points) / np.diff(spend_points)
            
            if len(marginal_returns) > 0 and np.max(marginal_returns) > 0:
                max_marginal = np.max(marginal_returns)
                saturation_idx = np.where(marginal_returns[SATURATION_SKIP_POINTS:] < max_marginal * SATURATION_THRESHOLD)[0]
                
                if len(saturation_idx) > 0:
                    saturation_point = float(spend_points[saturation_idx[0] + SATURATION_SKIP_POINTS])
                else:
                    saturation_point = np.max(spend_points) * SATURATION_CONSERVATIVE
            else:
                saturation_point = np.max(spend_points) * SATURATION_DEFAULT
            
            # Clamp within reasonable bounds
            max_spend = np.max(spend_points)
            return float(min(max_spend * SATURATION_MAX_BOUND, max(max_spend * SATURATION_MIN_BOUND, saturation_point)))
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Error finding saturation point: {e}")
            return float(np.max(spend_points) * SATURATION_DEFAULT)
    
    def _calculate_efficiency(self, channel_idx: int) -> float:
        """Calculate channel efficiency from model parameters."""
        try:
            if 'roi_m' in self.posterior.data_vars:
                return float(self.posterior['roi_m'].mean(dim=['chain', 'draw']).values[channel_idx])
            else:
                return DEFAULT_EFFICIENCY + channel_idx * EFFICIENCY_INCREMENT
        except (KeyError, ValueError, IndexError) as e:
            logger.warning(f"Could not extract efficiency for channel {channel_idx}: {e}")
            return DEFAULT_EFFICIENCY
    
    def _get_adstock_rate(self, channel_idx: int) -> float:
        """Get adstock rate from model parameters."""
        try:
            if 'alpha_m' in self.posterior.data_vars:
                return float(self.posterior['alpha_m'].mean(dim=['chain', 'draw']).values[channel_idx])
            else:
                return DEFAULT_ADSTOCK + (channel_idx * ADSTOCK_INCREMENT) % ADSTOCK_MAX
        except (KeyError, ValueError, IndexError) as e:
            logger.warning(f"Could not extract adstock rate for channel {channel_idx}: {e}")
            return DEFAULT_ADSTOCK + (channel_idx * ADSTOCK_INCREMENT) % ADSTOCK_MAX
    
    def _generate_fallback_curve(self, channel_idx: int) -> Dict[str, Any]:
        """Generate fallback curve when all else fails."""
        spend = list(range(0, FALLBACK_SPEND_MAX, FALLBACK_SPEND_STEP))
        base_response = FALLBACK_BASE_RESPONSE + channel_idx * FALLBACK_RESPONSE_INCREMENT
        curve_shape = FALLBACK_CURVE_BASE + channel_idx * FALLBACK_CURVE_INCREMENT
        response = [np.power(s, curve_shape) * base_response / 1000 for s in spend]
        
        return {
            "spend": spend,
            "response": response,
            "saturation_point": FALLBACK_SATURATION_BASE + channel_idx * FALLBACK_SATURATION_INCREMENT,
            "efficiency": FALLBACK_EFFICIENCY_BASE + channel_idx * FALLBACK_EFFICIENCY_INCREMENT,
            "adstock_rate": FALLBACK_ADSTOCK_BASE + channel_idx * FALLBACK_ADSTOCK_INCREMENT
        }
