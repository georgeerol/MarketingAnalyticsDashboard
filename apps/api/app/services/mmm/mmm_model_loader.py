"""
MMM model loading utilities.

Handles loading of Google Meridian models with fallback to synthetic models
for development and testing.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, List
from app.core.logging import get_logger
from .mmm_fallback_model import create_fallback_model

logger = get_logger(__name__)


class MMMModelError(Exception):
    """Exception raised for MMM model related errors."""
    pass


@lru_cache(maxsize=1)
def load_mmm_model(model_path: str) -> Any:
    """
    Load MMM model with caching and fallback support.
    
    Args:
        model_path: Path to the MMM model file
        
    Returns:
        Loaded MMM model (Google Meridian or fallback)
        
    Raises:
        MMMModelError: If model loading fails
    """
    model_path_obj = Path(model_path)
    if not model_path_obj.exists():
        raise MMMModelError(f"MMM model file not found at {model_path}")

    try:
        # Try to load with Google Meridian
        from meridian.model.model import load_mmm
        logger.info(f"Loading Google Meridian MMM model from {model_path}")
        model_data = load_mmm(str(model_path))
        logger.info("Successfully loaded Google Meridian MMM model")
        return model_data

    except ImportError:
        # Fallback to synthetic model
        logger.warning("Google Meridian not available; using lightweight fallback model for tests")
        return create_fallback_model()

    except Exception as e:
        logger.error(f"Error loading MMM model: {e}")
        raise MMMModelError(f"Failed to load MMM model: {str(e)}")


class ChannelNameExtractor:
    """Extracts channel names from different MMM model formats."""
    
    @staticmethod
    def extract_channel_names(model: Any) -> List[str]:
        """
        Extract channel names from the loaded model.
        
        Args:
            model: Loaded MMM model
            
        Returns:
            List of channel names
        """
        try:
            # Try different ways to get channel names from Meridian model
            if hasattr(model, 'input_data') and hasattr(model.input_data, 'media'):
                media_data = model.input_data.media
                if hasattr(media_data, 'columns'):
                    return list(media_data.columns)
                elif hasattr(media_data, 'coords') and 'media_channel' in media_data.coords:
                    return list(media_data.coords['media_channel'].values)
            
            # Try model specification
            if hasattr(model, 'model_spec') and hasattr(model.model_spec, 'media_names'):
                return list(model.model_spec.media_names)
            
            # Try n_media_channels and generate names
            if hasattr(model, 'n_media_channels'):
                n_channels = model.n_media_channels
                return [f"Channel_{i}" for i in range(n_channels)]
            
            # Final fallback
            logger.warning("Could not extract channel names from model, using defaults")
            return DEFAULT_CHANNEL_NAMES.copy()
            
        except Exception as e:
            logger.error(f"Error extracting channel names: {e}")
            return DEFAULT_CHANNEL_NAMES.copy()
    
    @staticmethod
    def validate_channel_names(channels: List[str]) -> List[str]:
        """
        Validate and clean channel names.
        
        Args:
            channels: List of channel names to validate
            
        Returns:
            List of validated channel names
        """
        if not channels:
            logger.warning("Empty channel list provided, using defaults")
            return DEFAULT_CHANNEL_NAMES.copy()
        
        validated = []
        for i, channel in enumerate(channels):
            if not isinstance(channel, str):
                logger.warning(f"Non-string channel name at index {i}: {channel}")
                validated.append(f"Channel{i}")
            elif not channel.strip():
                logger.warning(f"Empty channel name at index {i}")
                validated.append(f"Channel{i}")
            else:
                validated.append(channel.strip())
        
        if len(validated) != len(channels):
            logger.warning(f"Channel validation changed count: {len(channels)} -> {len(validated)}")
        
        return validated


def get_model_info(model: Any) -> dict:
    """
    Extract comprehensive information about the loaded model.
    
    Args:
        model: Loaded MMM model
        
    Returns:
        Dictionary with model information
    """
    if model is None:
        raise TypeError("Model cannot be None")
    
    info = {
        "model_type": "Unknown",
        "has_required_attributes": True,
        "missing_attributes": [],
        "channel_count": 0,
        "attributes": []
    }
    
    try:
        # Determine model type
        if hasattr(model, '__class__'):
            class_name = model.__class__.__name__
            if "Fallback" in class_name:
                info["model_type"] = "Fallback MMM Model"
            elif "Meridian" in class_name or "meridian" in str(type(model)).lower():
                info["model_type"] = "Google Meridian"
            else:
                info["model_type"] = class_name
        
        # Check attributes
        all_attributes = REQUIRED_MODEL_ATTRIBUTES + OPTIONAL_MODEL_ATTRIBUTES
        present_attributes = []
        missing_attributes = []
        
        for attr in all_attributes:
            if hasattr(model, attr):
                present_attributes.append(attr)
            else:
                missing_attributes.append(attr)
        
        info["attributes"] = present_attributes
        info["missing_attributes"] = missing_attributes
        info["has_required_attributes"] = all(
            hasattr(model, attr) for attr in REQUIRED_MODEL_ATTRIBUTES
        )
        
        # Get channel count
        try:
            channels = ChannelNameExtractor.extract_channel_names(model)
            info["channel_count"] = len(channels)
        except Exception:
            info["channel_count"] = 0
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        info["error"] = str(e)
    
    return info
