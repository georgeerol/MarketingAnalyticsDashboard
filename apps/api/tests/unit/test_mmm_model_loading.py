"""
Unit tests for MMM model loading and real Google Meridian integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import numpy as np
import sys

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.mmm_service import MMMService, MMMModelError
from app.schemas.mmm import MMMStatus, MMMModelInfo


class TestMMMModelLoading:
    """Test MMM model loading functionality."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_mmm_service_initialization(self):
        """Test MMM service initialization."""
        service = MMMService()
        
        assert service is not None
        assert service._model_data is None
        assert service._is_loaded is False
        assert service.model_path is not None
        assert isinstance(service.model_path, Path)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_model_path_configuration(self):
        """Test that model path is correctly configured."""
        service = MMMService()
        
        # Check that path ends with the expected model file
        assert str(service.model_path).endswith("saved_mmm.pkl")
        assert service.model_path.name == "saved_mmm.pkl"

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_model_status_file_exists(self, mock_exists):
        """Test model status when file exists."""
        mock_exists.return_value = True
        service = MMMService()
        
        status = service.get_model_status()
        
        assert isinstance(status, MMMStatus)
        assert status.status == "success"
        assert status.file_exists is True
        assert status.model_info is not None

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_model_status_file_missing(self, mock_exists):
        """Test model status when file is missing."""
        mock_exists.return_value = False
        service = MMMService()
        
        status = service.get_model_status()
        
        assert isinstance(status, MMMStatus)
        assert status.status == "error"
        assert status.file_exists is False
        assert "not found" in status.message

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_load_model_file_not_found(self, mock_exists):
        """Test model loading when file doesn't exist."""
        mock_exists.return_value = False
        service = MMMService()
        
        with pytest.raises(MMMModelError, match="MMM model file not found"):
            service._load_model()

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_load_model_success(self, mock_load_mmm, mock_exists):
        """Test successful model loading."""
        mock_exists.return_value = True
        
        # Create a mock Meridian model
        mock_model = Mock()
        mock_model.n_times = 156
        mock_model.n_media_channels = 5
        
        # Mock inference data with posterior
        mock_posterior = Mock()
        mock_posterior.data_vars = ['roi_m', 'alpha_m', 'beta_m']
        mock_inference_data = Mock()
        mock_inference_data.posterior = mock_posterior
        mock_model.inference_data = mock_inference_data
        
        # Mock media tensors
        mock_media_tensors = Mock()
        mock_spend_tensor = Mock()
        mock_spend_tensor.numpy.return_value = np.random.rand(40, 156, 5)
        mock_media_tensors.media_spend = mock_spend_tensor
        mock_model.media_tensors = mock_media_tensors
        
        mock_load_mmm.return_value = mock_model
        
        service = MMMService()
        loaded_model = service._load_model()
        
        assert loaded_model is not None
        assert service._is_loaded is True
        assert service._model_data is mock_model
        mock_load_mmm.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_load_model_meridian_not_available(self, mock_exists):
        """Test model loading when Meridian package is not available."""
        mock_exists.return_value = True
        
        service = MMMService()
        
        with patch('app.services.mmm_service.load_mmm', side_effect=ImportError("No module named 'meridian'")):
            with pytest.raises(MMMModelError, match="Google Meridian package not available"):
                service._load_model()

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_model_caching(self):
        """Test that model loading is cached."""
        service = MMMService()
        
        # Mock a loaded model
        mock_model = Mock()
        service._model_data = mock_model
        service._is_loaded = True
        
        # Second call should return cached model
        cached_model = service._load_model()
        assert cached_model is mock_model

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_channel_names_from_model(self, mock_load_mmm, mock_exists):
        """Test extracting channel names from model."""
        mock_exists.return_value = True
        
        # Create mock model with n_media_channels
        mock_model = Mock()
        mock_model.n_media_channels = 3
        mock_load_mmm.return_value = mock_model
        
        service = MMMService()
        channels = service._get_channel_names()
        
        assert isinstance(channels, list)
        assert len(channels) == 3
        assert all(channel.startswith("Channel") for channel in channels)

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_model_info_real_model(self, mock_load_mmm, mock_exists):
        """Test getting model info from real model."""
        mock_exists.return_value = True
        
        # Create comprehensive mock model
        mock_model = Mock()
        mock_model.n_times = 156
        mock_model.n_media_channels = 5
        mock_load_mmm.return_value = mock_model
        
        service = MMMService()
        info = service.get_model_info()
        
        assert isinstance(info, MMMModelInfo)
        assert info.model_type == "Google Meridian"
        assert info.data_source == "real_model"
        assert info.total_weeks == 156
        assert len(info.channels) == 5

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_basic_model_info(self):
        """Test getting basic model information."""
        service = MMMService()
        
        with patch.object(service.model_path, 'exists', return_value=True):
            with patch.object(service.model_path, 'stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                info = service._get_basic_model_info()
                
                assert isinstance(info, dict)
                assert "file_path" in info
                assert "file_exists" in info
                assert "file_size" in info
                assert info["file_exists"] is True
                assert info["file_size"] == 1024
                assert info["use_mock_data"] is False


class TestMMMModelDataExtraction:
    """Test data extraction from real MMM model."""

    @pytest.fixture
    def mock_meridian_model(self):
        """Create mock Meridian model for testing."""
        mock_model = Mock()
        
        # Basic model properties
        mock_model.n_times = 156
        mock_model.n_media_channels = 5
        
        # Mock inference data with posterior
        mock_posterior = Mock()
        mock_posterior.data_vars = ['roi_m', 'alpha_m', 'beta_m', 'contribution_n']
        
        # Mock ROI data
        mock_roi = Mock()
        mock_roi.mean.return_value.values = np.array([2.5, 1.8, 3.2, 2.1, 2.9])
        mock_posterior.__getitem__ = Mock(return_value=mock_roi)
        
        mock_inference_data = Mock()
        mock_inference_data.posterior = mock_posterior
        mock_model.inference_data = mock_inference_data
        
        # Mock media tensors
        mock_media_tensors = Mock()
        mock_spend_tensor = Mock()
        mock_spend_tensor.numpy.return_value = np.random.rand(40, 156, 5) * 1000
        mock_media_tensors.media_spend = mock_spend_tensor
        mock_model.media_tensors = mock_media_tensors
        
        return mock_model

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_contribution_data_real_calculation(self, mock_load_mmm, mock_exists, mock_meridian_model):
        """Test contribution data calculation from real model."""
        mock_exists.return_value = True
        mock_load_mmm.return_value = mock_meridian_model
        
        service = MMMService()
        contribution_data = service.get_contribution_data()
        
        assert isinstance(contribution_data, dict)
        assert "channels" in contribution_data
        assert "data" in contribution_data
        assert "summary" in contribution_data
        assert "shape" in contribution_data
        
        # Check that we have data for all channels
        assert len(contribution_data["channels"]) == 5
        assert len(contribution_data["data"]) == 5
        assert len(contribution_data["summary"]) == 5
        
        # Check data structure
        for channel in contribution_data["channels"]:
            assert channel in contribution_data["data"]
            assert channel in contribution_data["summary"]
            
            # Check that contribution data is a list of numbers
            channel_data = contribution_data["data"][channel]
            assert isinstance(channel_data, list)
            assert len(channel_data) == 156  # Should have 156 time periods
            
            # Check summary statistics
            summary = contribution_data["summary"][channel]
            assert "mean" in summary
            assert "total" in summary
            assert "max" in summary
            assert "min" in summary

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_contribution_data_specific_channel(self, mock_load_mmm, mock_exists, mock_meridian_model):
        """Test getting contribution data for a specific channel."""
        mock_exists.return_value = True
        mock_load_mmm.return_value = mock_meridian_model
        
        service = MMMService()
        contribution_data = service.get_contribution_data(channel="Channel0")
        
        assert len(contribution_data["channels"]) == 1
        assert contribution_data["channels"][0] == "Channel0"
        assert "Channel0" in contribution_data["data"]
        assert "Channel0" in contribution_data["summary"]

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_contribution_data_invalid_channel(self, mock_load_mmm, mock_exists, mock_meridian_model):
        """Test getting contribution data for invalid channel."""
        mock_exists.return_value = True
        mock_load_mmm.return_value = mock_meridian_model
        
        service = MMMService()
        
        with pytest.raises(MMMModelError, match="not found in model"):
            service.get_contribution_data(channel="InvalidChannel")

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_response_curves_real_model(self, mock_load_mmm, mock_exists, mock_meridian_model):
        """Test getting response curves from real model."""
        mock_exists.return_value = True
        mock_load_mmm.return_value = mock_meridian_model
        
        service = MMMService()
        curves_data = service.get_response_curves()
        
        assert isinstance(curves_data, dict)
        assert "curves" in curves_data
        assert len(curves_data["curves"]) == 5
        
        # Check curve structure for each channel
        for channel, curve in curves_data["curves"].items():
            assert "spend" in curve
            assert "response" in curve
            assert "saturation_point" in curve
            assert "efficiency" in curve
            assert "adstock_rate" in curve
            
            assert isinstance(curve["spend"], list)
            assert isinstance(curve["response"], list)
            assert len(curve["spend"]) == len(curve["response"])
            assert len(curve["spend"]) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_get_channel_summary_real_model(self, mock_load_mmm, mock_exists, mock_meridian_model):
        """Test getting channel summary from real model."""
        mock_exists.return_value = True
        mock_load_mmm.return_value = mock_meridian_model
        
        service = MMMService()
        summary = service.get_channel_summary()
        
        assert isinstance(summary, dict)
        assert len(summary) == 5
        
        # Check summary structure for each channel
        for channel, channel_summary in summary.items():
            assert hasattr(channel_summary, 'name')
            assert hasattr(channel_summary, 'total_spend')
            assert hasattr(channel_summary, 'total_contribution')
            assert hasattr(channel_summary, 'contribution_share')
            assert hasattr(channel_summary, 'efficiency')
            assert hasattr(channel_summary, 'avg_weekly_spend')
            assert hasattr(channel_summary, 'avg_weekly_contribution')
            
            assert channel_summary.name == channel
            assert channel_summary.total_spend >= 0
            assert channel_summary.total_contribution >= 0
            assert 0 <= channel_summary.contribution_share <= 1


class TestMMMModelErrorHandling:
    """Test error handling in MMM model operations."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_mmm_model_error_creation(self):
        """Test MMMModelError exception creation."""
        error_msg = "Test error message"
        error = MMMModelError(error_msg)
        
        assert isinstance(error, Exception)
        assert str(error) == error_msg

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_model_loading_exception_handling(self, mock_load_mmm, mock_exists):
        """Test handling of exceptions during model loading."""
        mock_exists.return_value = True
        mock_load_mmm.side_effect = Exception("Model loading failed")
        
        service = MMMService()
        
        with pytest.raises(MMMModelError, match="Failed to load MMM model"):
            service._load_model()

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_contribution_data_missing_roi(self, mock_load_mmm, mock_exists):
        """Test handling when ROI data is missing from model."""
        mock_exists.return_value = True
        
        # Create model without ROI data
        mock_model = Mock()
        mock_posterior = Mock()
        mock_posterior.data_vars = ['alpha_m', 'beta_m']  # No roi_m
        mock_inference_data = Mock()
        mock_inference_data.posterior = mock_posterior
        mock_model.inference_data = mock_inference_data
        
        mock_load_mmm.return_value = mock_model
        
        service = MMMService()
        
        with pytest.raises(MMMModelError, match="No ROI data found"):
            service.get_contribution_data()

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    def test_get_model_info_loading_error(self, mock_exists):
        """Test get_model_info when model loading fails."""
        mock_exists.return_value = True
        
        service = MMMService()
        
        with patch.object(service, '_load_model', side_effect=Exception("Loading failed")):
            with pytest.raises(MMMModelError, match="Failed to get model info"):
                service.get_model_info()


class TestMMMModelIntegration:
    """Integration tests for MMM model with realistic scenarios."""

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('app.services.mmm_service.Path.exists')
    @patch('meridian.model.model.load_mmm')
    def test_full_model_workflow(self, mock_load_mmm, mock_exists):
        """Test complete model workflow from loading to data extraction."""
        mock_exists.return_value = True
        
        # Create realistic mock model
        mock_model = Mock()
        mock_model.n_times = 156
        mock_model.n_media_channels = 5
        
        # Mock posterior with realistic data
        mock_posterior = Mock()
        mock_posterior.data_vars = ['roi_m', 'alpha_m', 'beta_m']
        
        mock_roi = Mock()
        mock_roi.mean.return_value.values = np.array([2.5, 1.8, 3.2, 2.1, 2.9])
        mock_posterior.__getitem__ = Mock(return_value=mock_roi)
        
        mock_inference_data = Mock()
        mock_inference_data.posterior = mock_posterior
        mock_model.inference_data = mock_inference_data
        
        # Mock media tensors with realistic spend data
        mock_media_tensors = Mock()
        mock_spend_tensor = Mock()
        spend_data = np.random.rand(40, 156, 5) * 1000  # Realistic spend values
        mock_spend_tensor.numpy.return_value = spend_data
        mock_media_tensors.media_spend = mock_spend_tensor
        mock_model.media_tensors = mock_media_tensors
        
        mock_load_mmm.return_value = mock_model
        
        service = MMMService()
        
        # Test complete workflow
        status = service.get_model_status()
        assert status.status == "success"
        
        info = service.get_model_info()
        assert info.model_type == "Google Meridian"
        assert info.data_source == "real_model"
        
        channels = service.get_channel_names()
        assert len(channels) == 5
        
        contribution = service.get_contribution_data()
        assert len(contribution["channels"]) == 5
        
        curves = service.get_response_curves()
        assert len(curves["curves"]) == 5
        
        summary = service.get_channel_summary()
        assert len(summary) == 5

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_service_state_consistency(self):
        """Test that service maintains consistent state across operations."""
        service = MMMService()
        
        # Initially not loaded
        assert service._is_loaded is False
        assert service._model_data is None
        
        # Mock successful loading
        mock_model = Mock()
        service._model_data = mock_model
        service._is_loaded = True
        
        # State should be maintained
        assert service._is_loaded is True
        assert service._model_data is mock_model
        
        # Subsequent calls should use cached model
        cached_model = service._load_model()
        assert cached_model is mock_model
