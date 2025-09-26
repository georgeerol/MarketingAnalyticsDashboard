"""
Unit tests for MMM model loading and data processing.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import sys

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mmm_utils import MMMModelLoader
from mmm_mock_data import generate_mock_mmm_data, get_mock_channels


class TestMMMModelLoader:
    """Test cases for MMMModelLoader class."""

    @pytest.mark.unit
    def test_init_default_path(self):
        """Test MMMModelLoader initialization with default path."""
        loader = MMMModelLoader()
        assert loader.model_path.name == "saved_mmm.pkl"
        assert not loader.use_mock_data
        assert loader._model_data is None

    @pytest.mark.unit
    def test_init_custom_path(self):
        """Test MMMModelLoader initialization with custom path."""
        custom_path = Path("/custom/path/model.pkl")
        loader = MMMModelLoader(model_path=custom_path)
        assert loader.model_path == custom_path

    @pytest.mark.unit
    def test_init_mock_data_flag(self):
        """Test MMMModelLoader initialization with mock data flag."""
        loader = MMMModelLoader(use_mock_data=True)
        assert loader.use_mock_data

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_load_model_mock_data(self, mock_mmm_loader):
        """Test loading model with mock data."""
        model_data = mock_mmm_loader.load_model()
        
        assert model_data is not None
        assert isinstance(model_data, dict)
        assert "model_info" in model_data
        assert "channels" in model_data["model_info"]

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_load_model_file_not_exists(self):
        """Test loading model when file doesn't exist."""
        non_existent_path = Path("/non/existent/path.pkl")
        loader = MMMModelLoader(model_path=non_existent_path)
        
        model_data = loader.load_model()
        
        # Should fallback to mock data
        assert model_data is not None
        assert isinstance(model_data, dict)

    @pytest.mark.unit
    @pytest.mark.mmm
    @patch('meridian.model.model.load_mmm')
    def test_load_model_real_meridian_success(self, mock_load_mmm, mmm_model_path):
        """Test successful loading of real Meridian model."""
        # Mock the Meridian model object
        mock_model = Mock()
        mock_model.__class__.__name__ = "Meridian"
        mock_load_mmm.return_value = mock_model
        
        loader = MMMModelLoader(model_path=mmm_model_path)
        
        # Mock file existence
        with patch.object(Path, 'exists', return_value=True):
            model_data = loader.load_model()
        
        assert model_data == mock_model
        mock_load_mmm.assert_called_once_with(str(mmm_model_path))

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_media_channels_mock_data(self, mock_mmm_loader):
        """Test getting media channels from mock data."""
        channels = mock_mmm_loader.get_media_channels()
        
        assert isinstance(channels, list)
        assert len(channels) > 0
        expected_channels = get_mock_channels()
        assert channels == expected_channels

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_media_channels_real_model(self):
        """Test getting media channels from real Meridian model."""
        # Mock a real Meridian model
        mock_model = Mock()
        mock_model.__class__.__module__ = "meridian.model.model"
        mock_model.n_media_channels = 5
        mock_model._input_data = Mock()
        # Provide actual media names to avoid fallback
        mock_model._input_data.media_names = ['Channel_1', 'Channel_2', 'Channel_3', 'Channel_4', 'Channel_5']
        
        loader = MMMModelLoader()
        loader._model_data = mock_model
        
        channels = loader.get_media_channels()
        
        assert isinstance(channels, list)
        assert len(channels) == 5
        assert all(channel.startswith("Channel_") for channel in channels)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_model_info_mock_data(self, mock_mmm_loader):
        """Test getting model info from mock data."""
        info = mock_mmm_loader.get_model_info()
        
        assert isinstance(info, dict)
        assert "file_path" in info
        assert "data_source" in info
        assert info["is_real_model"] == False

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_model_info_real_model(self, mmm_model_path):
        """Test getting model info from real Meridian model."""
        # Mock a real Meridian model
        mock_model = Mock()
        mock_model.__class__.__module__ = "meridian.model.model"
        
        loader = MMMModelLoader(model_path=mmm_model_path)
        loader._model_data = mock_model
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'stat') as mock_stat:
            mock_stat.return_value.st_size = 32 * 1024 * 1024  # 32MB
            
            info = loader.get_model_info()
        
        assert isinstance(info, dict)
        assert info["data_source"] == "real_meridian_model"
        assert info["is_real_model"] == True
        assert info["file_size_mb"] == 32.0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_contribution_data_mock(self, mock_mmm_loader):
        """Test getting contribution data from mock model."""
        contrib_data = mock_mmm_loader.get_contribution_data()
        
        assert contrib_data is not None
        assert isinstance(contrib_data, pd.DataFrame)
        assert len(contrib_data.columns) > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_contribution_data_real_model(self):
        """Test getting contribution data from real Meridian model."""
        # Mock a real Meridian model
        mock_model = Mock()
        mock_model.__class__.__module__ = "meridian.model.model"
        
        loader = MMMModelLoader()
        loader._model_data = mock_model
        
        # Mock the get_media_channels method
        with patch.object(loader, 'get_media_channels', return_value=['Channel_1', 'Channel_2']):
            contrib_data = loader.get_contribution_data()
        
        assert contrib_data is not None
        assert isinstance(contrib_data, pd.DataFrame)
        assert list(contrib_data.columns) == ['Channel_1', 'Channel_2']

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_response_curves_mock(self, mock_mmm_loader):
        """Test getting response curves from mock model."""
        curves = mock_mmm_loader.get_response_curves()
        
        assert curves is not None
        assert isinstance(curves, dict)
        # Mock data returns response curves directly, not nested under "curves" key
        # Check for channel names instead
        channels = mock_mmm_loader.get_media_channels()
        assert len(curves) > 0
        # At least some channels should have response curves
        assert any(channel in curves for channel in channels)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_response_curves_real_model(self):
        """Test getting response curves from real Meridian model."""
        # Mock a real Meridian model
        mock_model = Mock()
        mock_model.__class__.__module__ = "meridian.model.model"
        
        loader = MMMModelLoader()
        loader._model_data = mock_model
        
        # Mock the get_media_channels method
        with patch.object(loader, 'get_media_channels', return_value=['Channel_1', 'Channel_2']):
            curves = loader.get_response_curves()
        
        assert curves is not None
        assert isinstance(curves, dict)
        assert "curves" in curves
        assert len(curves["curves"]) == 2


class TestMMMDataProcessing:
    """Test cases for MMM data processing functions."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_generate_mock_mmm_data(self):
        """Test mock MMM data generation."""
        mock_data = generate_mock_mmm_data()
        
        assert isinstance(mock_data, dict)
        required_keys = ["model_info", "spend_data", "contribution_data", 
                        "response_curves", "channel_summary", "model_fit"]
        
        for key in required_keys:
            assert key in mock_data

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_mock_channels(self):
        """Test getting mock channel names."""
        channels = get_mock_channels()
        
        assert isinstance(channels, list)
        assert len(channels) == 10
        assert "Google_Search" in channels
        assert "Facebook" in channels

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_contribution_data_structure(self, sample_contribution_data):
        """Test contribution data has correct structure."""
        df = pd.DataFrame(sample_contribution_data)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df.columns) == 5
        assert all(col.startswith("Channel_") for col in df.columns)
        assert df.shape[0] > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_response_curves_structure(self, sample_response_curves):
        """Test response curves have correct structure."""
        curves = sample_response_curves
        
        assert "curves" in curves
        assert isinstance(curves["curves"], dict)
        
        for channel, curve_data in curves["curves"].items():
            assert "spend" in curve_data
            assert "response" in curve_data
            assert "saturation_point" in curve_data
            assert "efficiency" in curve_data
            assert len(curve_data["spend"]) == len(curve_data["response"])


class TestMMMErrorHandling:
    """Test error handling in MMM functionality."""

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_load_model_import_error(self, mmm_model_path):
        """Test handling of ImportError when Meridian package is missing."""
        loader = MMMModelLoader(model_path=mmm_model_path)
        
        with patch.object(Path, 'exists', return_value=True), \
             patch('meridian.model.model.load_mmm', side_effect=ImportError("No module named 'meridian'")):
            
            model_data = loader.load_model()
            
            # Should fallback to mock data
            assert model_data is not None
            assert isinstance(model_data, dict)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_load_model_generic_error(self, mmm_model_path):
        """Test handling of generic errors during model loading."""
        loader = MMMModelLoader(model_path=mmm_model_path)
        
        with patch.object(Path, 'exists', return_value=True), \
             patch('meridian.model.model.load_mmm', side_effect=Exception("Generic error")):
            
            model_data = loader.load_model()
            
            # Should fallback to mock data
            assert model_data is not None
            assert isinstance(model_data, dict)

    @pytest.mark.unit
    @pytest.mark.mmm
    def test_get_channels_no_model_loaded(self):
        """Test getting channels when no model is loaded."""
        loader = MMMModelLoader(use_mock_data=True)
        # Don't load the model
        
        channels = loader.get_media_channels()
        
        # Should still return channels (loads model automatically)
        assert isinstance(channels, list)
        assert len(channels) > 0
