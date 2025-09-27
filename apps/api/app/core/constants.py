"""
Application constants and configuration values.

This module centralizes all hardcoded values and magic numbers used throughout the application.
"""

from typing import Dict, Any


class APIConstants:
    """API-related constants."""
    
    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 100
    
    # User fields
    USER_NAME_MAX_LENGTH = 100
    COMPANY_MAX_LENGTH = 100


class MMMConstants:
    """MMM (Marketing Mix Modeling) related constants."""
    
    # Model metadata
    MODEL_VERSION = "1.0.0"
    DEFAULT_TIME_PERIODS = 156
    DEFAULT_GEO_COUNT = 40
    DEFAULT_CHANNEL_COUNT = 5
    
    # Response curve generation
    RESPONSE_CURVE_POINTS = 100
    
    # Hill saturation parameters
    HILL_EC_MIN_RATIO = 0.2  # Minimum EC as ratio of max spend
    HILL_EC_MAX_RATIO = 0.5  # Maximum EC as ratio of max spend
    HILL_EC_SCALE_FACTOR = 0.3  # Scale factor for EC adjustment
    
    HILL_SLOPE_MIN = 0.7
    HILL_SLOPE_MAX = 1.5
    HILL_SLOPE_BASE = 0.8
    HILL_SLOPE_CHANNEL_FACTOR = 0.1  # Per-channel slope variation
    HILL_SLOPE_ROI_FACTOR = 0.4  # ROI influence on slope
    
    # Response scaling factors
    RESPONSE_SCALE_FACTOR = 0.1
    RESPONSE_SCALE_ENHANCED = 0.15
    RESPONSE_SCALE_CONTRIB = 0.0001
    
    # Saturation point calculation
    SATURATION_THRESHOLD = 0.1  # 10% of max marginal returns
    SATURATION_SKIP_POINTS = 5  # Skip first N points for saturation calculation
    SATURATION_FALLBACK_MIN = 0.4  # 40% of max spend
    SATURATION_FALLBACK_MAX = 0.9  # 90% of max spend
    SATURATION_CHANNEL_FACTOR = 0.1  # Per-channel variation
    
    # Efficiency calculation
    EFFICIENCY_SAMPLE_POINTS = 20  # Number of points to sample for efficiency
    EFFICIENCY_MIN_VALUE = 0.001  # Minimum efficiency value
    EFFICIENCY_FALLBACK = 0.1  # Fallback efficiency value
    
    # Adstock parameters
    ADSTOCK_BASE_RATE = 0.2
    ADSTOCK_CHANNEL_FACTOR = 0.1
    ADSTOCK_MAX_RATE = 0.5
    
    # Performance thresholds
    HIGH_PERFORMER_THRESHOLD = 1.2  # 120% of average efficiency
    MAINTAIN_THRESHOLD = 1.3  # 130% of average efficiency
    UNDERPERFORMER_THRESHOLD = 1.0  # 100% of average efficiency
    
    # Fallback curve parameters
    FALLBACK_CURVE_SHAPE_BASE = 0.8
    FALLBACK_CURVE_SHAPE_FACTOR = 0.3
    FALLBACK_SATURATION_BASE = 40000
    FALLBACK_SATURATION_STEP = 8000
    FALLBACK_EFFICIENCY_BASE = 0.05
    FALLBACK_EFFICIENCY_STEP = 0.02
    
    # Mock data generation
    MOCK_DATA_MEAN = 1000
    MOCK_DATA_STD = 200


class NetworkConstants:
    """Network and service configuration."""
    
    # Default ports
    API_PORT = 8000
    WEB_PORT = 3000
    
    # Default hosts
    DEFAULT_API_HOST = "localhost"
    DEFAULT_WEB_HOST = "localhost"
    
    # URLs
    DEFAULT_API_URL = f"http://{DEFAULT_API_HOST}:{API_PORT}"
    DEFAULT_WEB_URL = f"http://{DEFAULT_WEB_HOST}:{WEB_PORT}"
    
    # CORS
    DEFAULT_ALLOWED_ORIGINS = [DEFAULT_WEB_URL]


class CacheConstants:
    """Caching configuration."""
    
    # LRU Cache sizes
    MODEL_CACHE_SIZE = 1  # Only cache one model at a time
    
    # Cache timeouts (in seconds)
    RESPONSE_CURVE_CACHE_TTL = 3600  # 1 hour
    CHANNEL_SUMMARY_CACHE_TTL = 1800  # 30 minutes
    
    # Performance thresholds
    SLOW_REQUEST_THRESHOLD_MS = 1000  # 1 second
    CACHE_HIT_TARGET_RATIO = 0.95  # 95% cache hit rate target


class ValidationConstants:
    """Data validation constants."""
    
    # Numeric ranges
    SPEND_MIN_VALUE = 0
    SPEND_MAX_VALUE = 1_000_000_000  # 1 billion
    
    ROI_MIN_VALUE = 0
    ROI_MAX_VALUE = 100  # 100x return
    
    EFFICIENCY_MIN_VALUE = 0
    EFFICIENCY_MAX_VALUE = 10  # 10x efficiency
    
    # String lengths
    CHANNEL_NAME_MAX_LENGTH = 50
    MODEL_NAME_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 500


# Convenience access to all constants
ALL_CONSTANTS: Dict[str, Any] = {
    "api": APIConstants,
    "mmm": MMMConstants,
    "network": NetworkConstants,
    "cache": CacheConstants,
    "validation": ValidationConstants,
}


def get_constant(category: str, name: str, default: Any = None) -> Any:
    """
    Get a constant value by category and name.
    
    Args:
        category: The constant category (e.g., 'mmm', 'api')
        name: The constant name
        default: Default value if not found
        
    Returns:
        The constant value or default
    """
    try:
        return getattr(ALL_CONSTANTS[category], name)
    except (KeyError, AttributeError):
        return default
