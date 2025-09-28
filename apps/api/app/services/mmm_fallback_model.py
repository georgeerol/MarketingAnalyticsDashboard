"""
Fallback MMM model for testing and development when Google Meridian is not available.

This provides a lightweight in-memory model that mimics the Google Meridian interface
with realistic synthetic data for development and testing purposes.
"""

import numpy as np
from typing import Any


class _PosteriorVar:
    """Mock posterior variable for fallback model."""
    
    def __init__(self, values: np.ndarray):
        self._values = np.asarray(values)

    def mean(self, dim=None):
        class _MeanResult:
            def __init__(self, vals: np.ndarray):
                self.values = np.asarray(vals)
        return _MeanResult(self._values)


class _Posterior:
    """Mock posterior distribution for fallback model."""
    
    def __init__(self, data_vars: dict):
        self.data_vars = data_vars
        
    def __getitem__(self, key: str) -> _PosteriorVar:
        return self.data_vars[key]


class _InferenceData:
    """Mock inference data container for fallback model."""
    
    def __init__(self, posterior: _Posterior):
        self.posterior = posterior


class _Tensor:
    """Mock tensor for fallback model."""
    
    def __init__(self, arr: np.ndarray):
        self._arr = np.asarray(arr)

    def numpy(self) -> np.ndarray:
        return np.asarray(self._arr)


class _MediaTensors:
    """Mock media tensors for fallback model."""
    
    def __init__(self, media_spend: np.ndarray):
        self.media_spend = _Tensor(media_spend)


class _Media:
    """Mock media data container for fallback model."""
    
    def __init__(self, columns):
        self.columns = columns


class _InputData:
    """Mock input data container for fallback model."""
    
    def __init__(self, media):
        self.media = media


class FallbackMMMModel:
    """
    Lightweight fallback MMM model for testing and development.
    
    Provides a realistic mock implementation of Google Meridian model interface
    with synthetic but statistically reasonable data.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize fallback model with synthetic data."""
        rng = np.random.default_rng(seed)
        
        # Model dimensions
        self.n_media_channels = 5
        self.n_times = 156
        
        # Generate realistic MMM parameters
        roi = rng.uniform(0.8, 1.8, size=self.n_media_channels)
        ec = rng.uniform(0.2, 0.6, size=self.n_media_channels)
        slope = rng.uniform(0.8, 1.4, size=self.n_media_channels)
        contr = rng.uniform(0.3, 0.8, size=self.n_media_channels)
        alpha = rng.uniform(0.2, 0.5, size=self.n_media_channels)

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
        geos = 40
        base = rng.uniform(500, 2500, size=(geos, self.n_times, self.n_media_channels))
        # Accumulate to make larger totals and ensure realistic max spend
        media_spend = base.cumsum(axis=1)
        self.media_tensors = _MediaTensors(media_spend)

        # Total spend: time x channels
        self.total_spend = media_spend.sum(axis=0)

        # Channel names
        channel_names = [f"Channel{i}" for i in range(self.n_media_channels)]
        self.input_data = _InputData(_Media(channel_names))


def create_fallback_model() -> FallbackMMMModel:
    """Create a new fallback MMM model instance."""
    return FallbackMMMModel()
