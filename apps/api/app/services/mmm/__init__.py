"""
MMM (Media Mix Modeling) service components.

This package contains modular components for handling Google Meridian MMM models:
- Model loading and caching
- Fallback synthetic models for testing
- Data processing and statistical analysis
- Response curve generation and analysis

The modular design enables easy testing, maintenance, and extension of MMM functionality.
"""

from .mmm_model_loader import load_mmm_model, ChannelNameExtractor, MMMModelError
from .mmm_fallback_model import create_fallback_model, FallbackMMMModel
from .mmm_data_processor import MMMDataProcessor
from .mmm_curve_generator import ResponseCurveGenerator

__all__ = [
    # Model loading
    "load_mmm_model",
    "ChannelNameExtractor", 
    "MMMModelError",
    
    # Fallback model
    "create_fallback_model",
    "FallbackMMMModel",
    
    # Data processing
    "MMMDataProcessor",
    
    # Curve generation
    "ResponseCurveGenerator",
]
