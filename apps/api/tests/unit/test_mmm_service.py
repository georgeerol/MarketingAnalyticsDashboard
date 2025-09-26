"""
Unit tests for MMM service functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.mmm_service import MMMService, MMMModelError
from app.schemas.mmm import MMMStatus, MMMModelInfo


class TestMMMService:
    """Test MMM service functionality."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_mmm_service_init(self):
        """Test MMM service initialization."""
        service = MMMService()
        
        assert service is not None
        assert service._model_data is None
        assert service._is_loaded is False

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_model_status_file_exists(self, mmm_service: MMMService):
        """Test getting model status when file exists."""
        with patch.object(mmm_service.model_path, 'exists', return_value=True):
            status = mmm_service.get_model_status()
            
            assert isinstance(status, MMMStatus)
            assert status.status == "success"
            assert status.file_exists is True

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_model_status_file_missing(self, mmm_service: MMMService):
        """Test getting model status when file is missing."""
        with patch.object(mmm_service.model_path, 'exists', return_value=False):
            status = mmm_service.get_model_status()
            
            assert isinstance(status, MMMStatus)
            assert status.status == "error"
            assert status.file_exists is False

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_channel_names(self, mmm_service: MMMService):
        """Test getting channel names."""
        channels = mmm_service.get_channel_names()
        
        assert isinstance(channels, list)
        assert len(channels) > 0
        assert all(isinstance(channel, str) for channel in channels)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_model_info_real_data(self, mmm_service: MMMService):
        """Test getting model info with real data."""
        info = mmm_service.get_model_info()
        
        assert isinstance(info, MMMModelInfo)
        assert info.model_type == "Google Meridian"
        assert info.data_source == "real_model"
        assert len(info.channels) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_contribution_data(self, mmm_service: MMMService):
        """Test getting contribution data."""
        data = mmm_service.get_contribution_data()
        
        assert isinstance(data, dict)
        assert "channels" in data
        assert "data" in data
        assert "summary" in data
        assert "shape" in data
        
        assert isinstance(data["channels"], list)
        assert len(data["channels"]) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_contribution_data_specific_channel(self, mmm_service: MMMService):
        """Test getting contribution data for specific channel."""
        channels = mmm_service.get_channel_names()
        if channels:
            channel = channels[0]
            data = mmm_service.get_contribution_data(channel)
            
            assert isinstance(data, dict)
            assert "channels" in data
            assert "data" in data
            assert "summary" in data

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_contribution_data_invalid_channel(self, mmm_service: MMMService):
        """Test getting contribution data for invalid channel."""
        with pytest.raises(MMMModelError, match="not found in model"):
            mmm_service.get_contribution_data("NonexistentChannel")

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_response_curves(self, mmm_service: MMMService):
        """Test getting response curves."""
        curves = mmm_service.get_response_curves()
        
        assert isinstance(curves, dict)
        assert "curves" in curves
        assert isinstance(curves["curves"], dict)
        assert len(curves["curves"]) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_response_curves_specific_channel(self, mmm_service: MMMService):
        """Test getting response curves for specific channel."""
        channels = mmm_service.get_channel_names()
        if channels:
            channel = channels[0]
            curves = mmm_service.get_response_curves(channel)
            
            assert isinstance(curves, dict)
            assert "curves" in curves
            assert channel in curves["curves"]

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_response_curves_invalid_channel(self, mmm_service: MMMService):
        """Test getting response curves for invalid channel."""
        with pytest.raises(MMMModelError, match="not found in model"):
            mmm_service.get_response_curves("NonexistentChannel")

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_channel_summary(self, mmm_service: MMMService):
        """Test getting channel summary."""
        summary = mmm_service.get_channel_summary()
        
        assert isinstance(summary, dict)
        assert len(summary) > 0
        
        # Check structure of summary data
        for channel, data in summary.items():
            assert hasattr(data, 'name')
            assert hasattr(data, 'total_spend')
            assert hasattr(data, 'total_contribution')
            assert hasattr(data, 'efficiency')

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_generate_response_curve(self, mmm_service: MMMService):
        """Test generating response curve for a channel."""
        channel = "TestChannel"
        curve = mmm_service._generate_response_curve(channel)
        
        assert isinstance(curve, dict)
        assert "spend" in curve
        assert "response" in curve
        assert "saturation_point" in curve
        assert "efficiency" in curve
        assert "adstock_rate" in curve
        
        assert isinstance(curve["spend"], list)
        assert isinstance(curve["response"], list)
        assert len(curve["spend"]) == len(curve["response"])

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_load_model_file_not_found(self, mock_exists, mmm_service: MMMService):
        """Test model loading when file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(MMMModelError, match="MMM model file not found"):
            mmm_service._load_model()

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.logger')
    def test_model_loading_error_handling(self, mock_logger, mmm_service: MMMService):
        """Test error handling during model loading."""
        with patch('meridian.model.model.load_mmm', side_effect=Exception("Test error")):
            with pytest.raises(MMMModelError, match="Failed to load MMM model"):
                mmm_service._load_model()

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_basic_model_info(self, mmm_service: MMMService):
        """Test getting basic model information."""
        info = mmm_service._get_basic_model_info()
        
        assert isinstance(info, dict)
        assert "file_path" in info
        assert "file_exists" in info
        assert "file_size" in info
        assert "file_path" in info


class TestMMMServiceErrorHandling:
    """Test MMM service error handling."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_mmm_model_error_inheritance(self):
        """Test that MMMModelError is properly defined."""
        error = MMMModelError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_service_handles_model_errors(self, mmm_service: MMMService):
        """Test that service properly handles model loading errors."""
        with patch.object(mmm_service, '_load_model', side_effect=Exception("Model error")):
            with pytest.raises(MMMModelError):
                mmm_service.get_model_info()


class TestMMMServiceIntegration:
    """Integration tests for MMM service with real-like scenarios."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_full_workflow_real_data(self, mmm_service: MMMService):
        """Test complete workflow with real model data."""
        # Test status
        status = mmm_service.get_model_status()
        assert status.status == "success"
        
        # Test model info
        info = mmm_service.get_model_info()
        assert info.data_source == "real_model"
        
        # Test channels
        channels = mmm_service.get_channel_names()
        assert len(channels) > 0
        
        # Test contribution data
        contribution = mmm_service.get_contribution_data()
        assert len(contribution["channels"]) > 0
        
        # Test response curves
        curves = mmm_service.get_response_curves()
        assert len(curves["curves"]) > 0
        
        # Test channel summary
        summary = mmm_service.get_channel_summary()
        assert len(summary) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_caching_behavior(self, mmm_service: MMMService):
        """Test that model loading is cached."""
        # First call should load the model
        model1 = mmm_service._load_model()
        assert mmm_service._is_loaded is True
        
        # Second call should return cached model
        model2 = mmm_service._load_model()
        assert model1 is model2  # Should be the same object
