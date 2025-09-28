"""
Fallback MMM model for testing and development when Google Meridian is not available.

This provides a lightweight in-memory model that mimics the Google Meridian interface
with realistic synthetic data for development and testing purposes.
"""

import numpy as np
from typing import Any, Dict, List, Optional, Union
from app.core.logging import get_logger

logger = get_logger(__name__)

# Model dimension constants
DEFAULT_MEDIA_CHANNELS = 5
DEFAULT_TIME_PERIODS = 156  # 3 years of weekly data
DEFAULT_GEOS = 40
DEFAULT_SEED = 42

# MMM parameter ranges (based on industry standards)
ROI_MIN = 0.8
ROI_MAX = 1.8
EC_MIN = 0.2  # Effective concentration minimum
EC_MAX = 0.6  # Effective concentration maximum
SLOPE_MIN = 0.8  # Hill curve slope minimum
SLOPE_MAX = 1.4  # Hill curve slope maximum
CONTRIBUTION_MIN = 0.3  # Contribution coefficient minimum
CONTRIBUTION_MAX = 0.8  # Contribution coefficient maximum
ADSTOCK_MIN = 0.2  # Adstock rate minimum
ADSTOCK_MAX = 0.5  # Adstock rate maximum

# Media spend generation parameters
SPEND_BASE_MIN = 500.0
SPEND_BASE_MAX = 2500.0


class _PosteriorVar:
    """Mock posterior variable for fallback model."""
    
    def __init__(self, values: Union[np.ndarray, List[float]]):
        if not isinstance(values, (np.ndarray, list)):
            raise TypeError(f"Values must be numpy array or list, got {type(values)}")
        self._values = np.asarray(values)
        if self._values.size == 0:
            raise ValueError("Values array cannot be empty")

    def mean(self, dim: Optional[Union[str, List[str]]] = None) -> '_MeanResult':
        """Return mean values, ignoring dim parameter for compatibility."""
        class _MeanResult:
            def __init__(self, vals: np.ndarray):
                self.values = np.asarray(vals)
        return _MeanResult(self._values)


class _Posterior:
    """Mock posterior distribution for fallback model."""
    
    def __init__(self, data_vars: Dict[str, _PosteriorVar]):
        if not isinstance(data_vars, dict):
            raise TypeError("data_vars must be a dictionary")
        if not data_vars:
            raise ValueError("data_vars cannot be empty")
        self.data_vars = data_vars
        
    def __getitem__(self, key: str) -> _PosteriorVar:
        if key not in self.data_vars:
            raise KeyError(f"Parameter '{key}' not found in posterior data")
        return self.data_vars[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if parameter exists in posterior data."""
        return key in self.data_vars


class _InferenceData:
    """Mock inference data container for fallback model."""
    
    def __init__(self, posterior: _Posterior):
        if not isinstance(posterior, _Posterior):
            raise TypeError(f"posterior must be _Posterior instance, got {type(posterior)}")
        self.posterior = posterior


class _Tensor:
    """Mock tensor for fallback model."""
    
    def __init__(self, arr: Union[np.ndarray, List]):
        if not isinstance(arr, (np.ndarray, list)):
            raise TypeError(f"Array must be numpy array or list, got {type(arr)}")
        self._arr = np.asarray(arr)
        if self._arr.size == 0:
            raise ValueError("Tensor array cannot be empty")

    def numpy(self) -> np.ndarray:
        """Return numpy array representation."""
        return np.asarray(self._arr)
    
    @property
    def shape(self) -> tuple:
        """Return tensor shape."""
        return self._arr.shape


class _MediaTensors:
    """Mock media tensors for fallback model."""
    
    def __init__(self, media_spend: Union[np.ndarray, List]):
        if not isinstance(media_spend, (np.ndarray, list)):
            raise TypeError(f"media_spend must be numpy array or list, got {type(media_spend)}")
        spend_array = np.asarray(media_spend)
        if spend_array.ndim < 3:
            raise ValueError(f"media_spend must be 3D (geos x time x channels), got {spend_array.ndim}D")
        self.media_spend = _Tensor(spend_array)


class _Media:
    """Mock media data container for fallback model."""
    
    def __init__(self, columns: List[str]):
        if not isinstance(columns, list):
            raise TypeError(f"columns must be a list, got {type(columns)}")
        if not columns:
            raise ValueError("columns cannot be empty")
        if not all(isinstance(col, str) for col in columns):
            raise TypeError("All columns must be strings")
        self.columns = columns


class _InputData:
    """Mock input data container for fallback model."""
    
    def __init__(self, media: _Media):
        if not isinstance(media, _Media):
            raise TypeError(f"media must be _Media instance, got {type(media)}")
        self.media = media


class FallbackMMMModel:
    """
    Lightweight fallback MMM model for testing and development.
    
    Provides a realistic mock implementation of Google Meridian model interface
    with synthetic but statistically reasonable data.
    
    Args:
        seed: Random seed for reproducible data generation
        n_channels: Number of media channels (default: 5)
        n_times: Number of time periods (default: 156 weeks)
        n_geos: Number of geographic regions (default: 40)
    """
    
    def __init__(self, seed: int = DEFAULT_SEED, n_channels: int = DEFAULT_MEDIA_CHANNELS, 
                 n_times: int = DEFAULT_TIME_PERIODS, n_geos: int = DEFAULT_GEOS):
        """Initialize fallback model with synthetic data."""
        # Validate inputs
        if not isinstance(seed, int) or seed < 0:
            raise ValueError(f"seed must be a non-negative integer, got {seed}")
        if not isinstance(n_channels, int) or n_channels <= 0:
            raise ValueError(f"n_channels must be a positive integer, got {n_channels}")
        if not isinstance(n_times, int) or n_times <= 0:
            raise ValueError(f"n_times must be a positive integer, got {n_times}")
        if not isinstance(n_geos, int) or n_geos <= 0:
            raise ValueError(f"n_geos must be a positive integer, got {n_geos}")
            
        logger.info(f"Initializing fallback MMM model: {n_channels} channels, {n_times} time periods, {n_geos} geos, seed={seed}")
        
        rng = np.random.default_rng(seed)
        
        # Model dimensions
        self.n_media_channels = n_channels
        self.n_times = n_times
        
        # Generate realistic MMM parameters using industry-standard ranges
        roi = rng.uniform(ROI_MIN, ROI_MAX, size=self.n_media_channels)
        ec = rng.uniform(EC_MIN, EC_MAX, size=self.n_media_channels)
        slope = rng.uniform(SLOPE_MIN, SLOPE_MAX, size=self.n_media_channels)
        contr = rng.uniform(CONTRIBUTION_MIN, CONTRIBUTION_MAX, size=self.n_media_channels)
        alpha = rng.uniform(ADSTOCK_MIN, ADSTOCK_MAX, size=self.n_media_channels)
        
        # Validate generated parameters
        self._validate_parameters(roi, ec, slope, contr, alpha)

        # Create posterior distribution
        posterior = _Posterior({
            'roi_m': _PosteriorVar(roi),
            'ec_m': _PosteriorVar(ec),
            'slope_m': _PosteriorVar(slope),
            'contr_coef': _PosteriorVar(contr),
            'alpha_m': _PosteriorVar(alpha),
        })

        self.inference_data = _InferenceData(posterior)

        # Generate realistic media spend data: geo x time x channels
        try:
            base = rng.uniform(SPEND_BASE_MIN, SPEND_BASE_MAX, size=(n_geos, self.n_times, self.n_media_channels))
            # Accumulate to make larger totals and ensure realistic max spend
            media_spend = base.cumsum(axis=1)
            
            # Validate spend data
            if np.any(media_spend < 0):
                raise ValueError("Generated negative media spend values")
            if np.any(np.isnan(media_spend)) or np.any(np.isinf(media_spend)):
                raise ValueError("Generated invalid (NaN/Inf) media spend values")
                
            self.media_tensors = _MediaTensors(media_spend)

            # Total spend: time x channels
            self.total_spend = media_spend.sum(axis=0)

            # Channel names
            channel_names = [f"Channel{i}" for i in range(self.n_media_channels)]
            self.input_data = _InputData(_Media(channel_names))
            
            logger.info(f"Generated fallback model with spend range: ${np.min(media_spend):.0f} - ${np.max(media_spend):.0f}")
            
        except Exception as e:
            logger.error(f"Error generating fallback model data: {e}")
            raise ValueError(f"Failed to generate fallback model: {e}")


    def _validate_parameters(self, roi: np.ndarray, ec: np.ndarray, slope: np.ndarray, 
                           contr: np.ndarray, alpha: np.ndarray) -> None:
        """Validate generated MMM parameters are within expected ranges."""
        validations = [
            (roi, "ROI", ROI_MIN, ROI_MAX),
            (ec, "EC", EC_MIN, EC_MAX),
            (slope, "Slope", SLOPE_MIN, SLOPE_MAX),
            (contr, "Contribution", CONTRIBUTION_MIN, CONTRIBUTION_MAX),
            (alpha, "Adstock", ADSTOCK_MIN, ADSTOCK_MAX)
        ]
        
        for param, name, min_val, max_val in validations:
            if np.any(param < min_val) or np.any(param > max_val):
                logger.warning(f"{name} parameters outside expected range [{min_val}, {max_val}]")
            if np.any(np.isnan(param)) or np.any(np.isinf(param)):
                raise ValueError(f"Invalid {name} parameters generated (NaN/Inf)")
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary information about the fallback model."""
        return {
            "model_type": "Fallback MMM Model",
            "n_channels": self.n_media_channels,
            "n_times": self.n_times,
            "channel_names": self.input_data.media.columns,
            "total_spend_range": {
                "min": float(np.min(self.total_spend)),
                "max": float(np.max(self.total_spend))
            },
            "parameters": {
                "roi_range": [ROI_MIN, ROI_MAX],
                "ec_range": [EC_MIN, EC_MAX],
                "slope_range": [SLOPE_MIN, SLOPE_MAX],
                "contribution_range": [CONTRIBUTION_MIN, CONTRIBUTION_MAX],
                "adstock_range": [ADSTOCK_MIN, ADSTOCK_MAX]
            }
        }


def create_fallback_model(seed: int = DEFAULT_SEED, n_channels: int = DEFAULT_MEDIA_CHANNELS,
                         n_times: int = DEFAULT_TIME_PERIODS, n_geos: int = DEFAULT_GEOS) -> FallbackMMMModel:
    """
    Create a new fallback MMM model instance.
    
    Args:
        seed: Random seed for reproducible generation
        n_channels: Number of media channels
        n_times: Number of time periods
        n_geos: Number of geographic regions
        
    Returns:
        Configured fallback MMM model
        
    Raises:
        ValueError: If parameters are invalid
    """
    try:
        return FallbackMMMModel(seed=seed, n_channels=n_channels, n_times=n_times, n_geos=n_geos)
    except Exception as e:
        logger.error(f"Failed to create fallback model: {e}")
        raise
