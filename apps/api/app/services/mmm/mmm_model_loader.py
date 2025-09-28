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
            return ["Google_Search", "Google_Display", "Facebook", "Instagram", "YouTube"]
            
        except Exception as e:
            logger.error(f"Error extracting channel names: {e}")
            return ["Google_Search", "Google_Display", "Facebook", "Instagram", "YouTube"]
