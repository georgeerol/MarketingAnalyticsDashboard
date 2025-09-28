"""
Simplified MMM service using modular components.

Main service class that coordinates MMM model operations using
specialized components for model loading, data processing, and curve generation.
"""

from typing import Dict, Any, Optional, List

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.mmm import MMMModelInfo, MMMChannelSummary
from app.services.mmm_model_loader import load_mmm_model, ChannelNameExtractor, MMMModelError
from app.services.mmm_data_processor import MMMDataProcessor
from app.services.mmm_curve_generator import ResponseCurveGenerator

settings = get_settings()
logger = get_logger(__name__)


class MMMService:
    """Simplified MMM service using modular components."""
    
    def __init__(self):
        self.model_path = settings.MMM_MODEL_FULL_PATH
        self._model = None
        self._channel_names = None
        self._data_processor = None
        self._curve_generator = None
    
    def get_model_info(self) -> MMMModelInfo:
        """Get model metadata like channels, training period, etc."""
        try:
            model = self._get_model()
            channels = self.get_channel_names()
            
            # Get model specification details
            n_times = getattr(model, 'n_times', 104)
            
            return MMMModelInfo(
                model_type="Google Meridian",
                version="1.0.0",
                training_period="2022-01-01 to 2024-01-01",
                channels=channels,
                data_frequency="weekly",
                total_weeks=n_times,
                data_source="real_model"
            )
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise MMMModelError(f"Failed to get model info: {str(e)}")
    
    def get_channel_names(self) -> List[str]:
        """Get list of channel names from the model."""
        try:
            if self._channel_names is None:
                model = self._get_model()
                self._channel_names = ChannelNameExtractor.extract_channel_names(model)
            return self._channel_names
        except Exception as e:
            logger.error(f"Error getting channel names: {e}")
            raise MMMModelError(f"Failed to get channel names: {str(e)}")
    
    def get_contribution_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get contribution data for channels."""
        try:
            data_processor = self._get_data_processor()
            return data_processor.get_contribution_data(channel)
        except Exception as e:
            logger.error(f"Error getting contribution data: {e}")
            raise MMMModelError(f"Failed to get contribution data: {str(e)}")
    
    def get_response_curves(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get response curve data for channels."""
        try:
            curve_generator = self._get_curve_generator()
            channels = self.get_channel_names()
            
            if channel and channel not in channels:
                raise MMMModelError(f"Channel '{channel}' not found in model")
            
            curves = {}
            target_channels = [channel] if channel else channels
            
            for ch in target_channels:
                curves[ch] = curve_generator.generate_curve(ch)
            
            return {"curves": curves}
            
        except Exception as e:
            logger.error(f"Error getting response curves: {e}")
            raise MMMModelError(f"Failed to get response curves: {str(e)}")
    
    def get_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """Get summary statistics for all channels."""
        try:
            data_processor = self._get_data_processor()
            return data_processor.get_channel_summary()
        except Exception as e:
            logger.error(f"Error getting channel summary: {e}")
            raise MMMModelError(f"Failed to get channel summary: {str(e)}")
    
    def _get_model(self) -> Any:
        """Get the loaded MMM model (cached)."""
        if self._model is None:
            self._model = load_mmm_model(str(self.model_path))
        return self._model
    
    def _get_data_processor(self) -> MMMDataProcessor:
        """Get the data processor (cached)."""
        if self._data_processor is None:
            model = self._get_model()
            channel_names = self.get_channel_names()
            self._data_processor = MMMDataProcessor(model, channel_names)
        return self._data_processor
    
    def _get_curve_generator(self) -> ResponseCurveGenerator:
        """Get the curve generator (cached)."""
        if self._curve_generator is None:
            model = self._get_model()
            channel_names = self.get_channel_names()
            self._curve_generator = ResponseCurveGenerator(model, channel_names)
        return self._curve_generator