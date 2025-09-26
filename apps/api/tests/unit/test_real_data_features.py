"""
Unit tests for real Google Meridian model data features.
Tests the enhanced response curve generation and real parameter extraction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import numpy as np

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.mmm_service import MMMService, MMMModelError


class TestRealDataFeatures:
    """Test real Google Meridian model data features."""

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_real_hill_parameters_extraction(self, mmm_service: MMMService):
        """Test extraction of real Hill saturation parameters from model."""
        # Mock a model with real Hill parameters
        mock_model = Mock()
        mock_posterior = Mock()
        
        # Mock Hill parameters (ec_m and slope_m)
        mock_posterior.data_vars = {
            'ec_m': Mock(),
            'slope_m': Mock(), 
            'roi_m': Mock(),
            'alpha_m': Mock()
        }
        
        # Mock parameter values for 5 channels
        ec_values = np.array([30457.38, 33918.16, 33350.92, 47599.59, 43482.25])
        slope_values = np.array([1.2, 0.8, 1.5, 0.9, 1.1])
        roi_values = np.array([1.50, 0.92, 1.43, 0.83, 1.58])
        alpha_values = np.array([0.77, 0.64, 0.40, 0.48, 0.83])
        
        # Mock the mean() method chain
        mock_posterior['ec_m'].mean.return_value.values = ec_values
        mock_posterior['slope_m'].mean.return_value.values = slope_values
        mock_posterior['roi_m'].mean.return_value.values = roi_values
        mock_posterior['alpha_m'].mean.return_value.values = alpha_values
        
        mock_model.inference_data.posterior = mock_posterior
        
        # Mock media tensors for spend data
        mock_media_tensors = Mock()
        mock_media_spend = Mock()
        mock_media_spend.numpy.return_value = np.random.rand(10, 156, 5) * 50000  # geo x time x channel
        mock_media_tensors.media_spend = mock_media_spend
        mock_model.media_tensors = mock_media_tensors
        
        with patch.object(mmm_service, '_load_model', return_value=mock_model):
            # Test response curve generation for first channel
            curve = mmm_service._generate_response_curve_from_model(mock_model, "Channel0")
            
            assert isinstance(curve, dict)
            assert "spend" in curve
            assert "response" in curve
            assert "saturation_point" in curve
            assert "efficiency" in curve
            assert "adstock_rate" in curve
            
            # Verify real parameters are used
            assert curve["efficiency"] == pytest.approx(1.50, rel=1e-2)  # Real ROI
            assert curve["adstock_rate"] == pytest.approx(0.77, rel=1e-2)  # Real alpha
            
            # Verify curve structure
            assert len(curve["spend"]) == 100  # Enhanced resolution
            assert len(curve["response"]) == 100
            assert len(curve["spend"]) == len(curve["response"])

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_channel_specific_parameters(self, mmm_service: MMMService):
        """Test that different channels get different parameters."""
        mock_model = Mock()
        mock_posterior = Mock()
        
        mock_posterior.data_vars = {
            'ec_m': Mock(),
            'slope_m': Mock(), 
            'roi_m': Mock(),
            'alpha_m': Mock()
        }
        
        # Different values for each channel
        ec_values = np.array([30000, 35000, 40000, 45000, 50000])
        slope_values = np.array([1.0, 1.2, 0.8, 1.5, 0.9])
        roi_values = np.array([1.50, 0.92, 1.43, 0.83, 1.58])
        alpha_values = np.array([0.77, 0.64, 0.40, 0.48, 0.83])
        
        mock_posterior['ec_m'].mean.return_value.values = ec_values
        mock_posterior['slope_m'].mean.return_value.values = slope_values
        mock_posterior['roi_m'].mean.return_value.values = roi_values
        mock_posterior['alpha_m'].mean.return_value.values = alpha_values
        
        mock_model.inference_data.posterior = mock_posterior
        
        # Mock media tensors
        mock_media_tensors = Mock()
        mock_media_spend = Mock()
        mock_media_spend.numpy.return_value = np.random.rand(10, 156, 5) * 50000
        mock_media_tensors.media_spend = mock_media_spend
        mock_model.media_tensors = mock_media_tensors
        
        with patch.object(mmm_service, '_load_model', return_value=mock_model):
            # Generate curves for different channels
            curve0 = mmm_service._generate_response_curve_from_model(mock_model, "Channel0")
            curve1 = mmm_service._generate_response_curve_from_model(mock_model, "Channel1")
            curve4 = mmm_service._generate_response_curve_from_model(mock_model, "Channel4")
            
            # Verify different efficiency values
            assert curve0["efficiency"] != curve1["efficiency"]
            assert curve1["efficiency"] != curve4["efficiency"]
            assert curve0["efficiency"] != curve4["efficiency"]
            
            # Verify different adstock rates
            assert curve0["adstock_rate"] != curve1["adstock_rate"]
            assert curve1["adstock_rate"] != curve4["adstock_rate"]
            
            # Verify Channel4 has highest efficiency (as per real data)
            assert curve4["efficiency"] > curve1["efficiency"]
            assert curve4["efficiency"] > curve0["efficiency"]

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_fallback_when_parameters_missing(self, mmm_service: MMMService):
        """Test fallback behavior when real parameters are not available."""
        mock_model = Mock()
        mock_posterior = Mock()
        
        # Mock model without Hill parameters
        mock_posterior.data_vars = {
            'roi_m': Mock()  # Only ROI available
        }
        
        roi_values = np.array([1.50, 0.92, 1.43, 0.83, 1.58])
        mock_posterior['roi_m'].mean.return_value.values = roi_values
        
        mock_model.inference_data.posterior = mock_posterior
        
        # Mock media tensors
        mock_media_tensors = Mock()
        mock_media_spend = Mock()
        mock_media_spend.numpy.return_value = np.random.rand(10, 156, 5) * 50000
        mock_media_tensors.media_spend = mock_media_spend
        mock_model.media_tensors = mock_media_tensors
        
        # Mock contribution data for fallback
        with patch.object(mmm_service, '_load_model', return_value=mock_model):
            with patch.object(mmm_service, 'get_contribution_data') as mock_contrib:
                mock_contrib.return_value = {
                    'summary': {
                        'Channel0': {'total': 1000000}
                    }
                }
                
                curve = mmm_service._generate_response_curve_from_model(mock_model, "Channel0")
                
                # Should still generate valid curve
                assert isinstance(curve, dict)
                assert "efficiency" in curve
                assert "adstock_rate" in curve
                assert curve["efficiency"] > 0

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_debug_model_parameters(self, mmm_service: MMMService):
        """Test the debug functionality for model parameters."""
        mock_model = Mock()
        mock_posterior = Mock()
        
        mock_posterior.data_vars = {
            'ec_m': Mock(),
            'slope_m': Mock(), 
            'roi_m': Mock(),
            'alpha_m': Mock(),
            'beta_m': Mock()
        }
        
        # Mock shapes and sample values
        for var in ['ec_m', 'slope_m', 'roi_m', 'alpha_m']:
            mock_var = Mock()
            mock_var.shape = (10, 1000, 5)  # chains x draws x channels
            mock_var.mean.return_value.values = np.array([1.0, 2.0, 3.0])
            mock_posterior[var] = mock_var
        
        mock_model.inference_data.posterior = mock_posterior
        
        # Mock model attributes
        model_attrs = ['adstock_hill_media', 'inference_data', 'media_tensors', 'n_media_channels']
        
        with patch('builtins.dir', return_value=model_attrs):
            debug_info = mmm_service._debug_model_parameters(mock_model)
            
            assert isinstance(debug_info, dict)
            assert "available_posterior_vars" in debug_info
            assert "model_attributes" in debug_info
            
            # Check that key variables are detected
            assert 'ec_m' in debug_info["available_posterior_vars"]
            assert 'slope_m' in debug_info["available_posterior_vars"]
            assert 'roi_m' in debug_info["available_posterior_vars"]
            
            # Check shapes are captured
            assert "roi_m_shape" in debug_info
            assert "ec_m_shape" in debug_info

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_enhanced_response_curves_structure(self, mmm_service: MMMService):
        """Test that enhanced response curves have correct structure."""
        curves = mmm_service.get_response_curves()
        
        assert isinstance(curves, dict)
        assert "curves" in curves
        
        for channel, curve_data in curves["curves"].items():
            # Verify all required fields
            assert "spend" in curve_data
            assert "response" in curve_data
            assert "saturation_point" in curve_data
            assert "efficiency" in curve_data
            assert "adstock_rate" in curve_data
            
            # Verify data types
            assert isinstance(curve_data["spend"], list)
            assert isinstance(curve_data["response"], list)
            assert isinstance(curve_data["saturation_point"], (int, float))
            assert isinstance(curve_data["efficiency"], (int, float))
            assert isinstance(curve_data["adstock_rate"], (int, float))
            
            # Verify positive values
            assert curve_data["efficiency"] > 0
            assert curve_data["saturation_point"] > 0
            assert 0 <= curve_data["adstock_rate"] <= 1
            
            # Verify enhanced resolution (100 points vs old 50)
            assert len(curve_data["spend"]) == 100
            assert len(curve_data["response"]) == 100

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_efficiency_differences_across_channels(self, mmm_service: MMMService):
        """Test that channels have meaningfully different efficiency values."""
        curves = mmm_service.get_response_curves()
        
        efficiencies = []
        for channel, curve_data in curves["curves"].items():
            efficiencies.append(curve_data["efficiency"])
        
        # Should have at least 2 channels
        assert len(efficiencies) >= 2
        
        # Efficiencies should not all be the same (old bug)
        unique_efficiencies = set(round(eff, 3) for eff in efficiencies)
        assert len(unique_efficiencies) > 1, "All channels have the same efficiency - real data not working"
        
        # Should have reasonable range (not all tiny differences)
        max_eff = max(efficiencies)
        min_eff = min(efficiencies)
        efficiency_range = max_eff - min_eff
        
        # Expect at least 20% difference between best and worst
        assert efficiency_range > 0.2, f"Efficiency range too small: {efficiency_range}"

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_saturation_points_vary_by_channel(self, mmm_service: MMMService):
        """Test that saturation points are different across channels."""
        curves = mmm_service.get_response_curves()
        
        saturation_points = []
        for channel, curve_data in curves["curves"].items():
            saturation_points.append(curve_data["saturation_point"])
        
        # Should have meaningful variation in saturation points
        unique_saturations = set(round(sp, 0) for sp in saturation_points)
        assert len(unique_saturations) > 1, "All channels have same saturation point"
        
        # Should be in reasonable range (not all tiny or all huge)
        max_sat = max(saturation_points)
        min_sat = min(saturation_points)
        
        assert min_sat > 100, "Saturation points too low"
        assert max_sat < 1000000, "Saturation points too high"
        assert max_sat > min_sat * 1.5, "Saturation points not varied enough"


class TestRealDataIntegration:
    """Integration tests for real data features."""

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_contribution_and_efficiency_consistency(self, mmm_service: MMMService):
        """Test that contribution data and efficiency data are consistent."""
        # Get both contribution and response curve data
        contribution = mmm_service.get_contribution_data()
        curves = mmm_service.get_response_curves()
        summary = mmm_service.get_channel_summary()
        
        # Should have same channels in all datasets
        contrib_channels = set(contribution["channels"])
        curve_channels = set(curves["curves"].keys())
        summary_channels = set(summary.keys())
        
        assert contrib_channels == curve_channels == summary_channels
        
        # Efficiency values should be consistent
        for channel in contrib_channels:
            summary_efficiency = summary[channel].efficiency
            curve_efficiency = curves["curves"][channel]["efficiency"]
            
            # Should be the same (or very close due to floating point)
            assert abs(summary_efficiency - curve_efficiency) < 0.001

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_real_vs_mock_data_detection(self, mmm_service: MMMService):
        """Test that we can detect we're using real vs mock data."""
        info = mmm_service.get_model_info()
        
        # Should indicate real data source
        assert info.data_source == "real_model"
        assert info.model_type == "Google Meridian"
        
        # Should have reasonable number of channels (not mock defaults)
        assert len(info.channels) >= 3
        assert len(info.channels) <= 10  # Reasonable upper bound
        
        # Should have reasonable time period
        assert info.total_weeks > 50  # At least a year of data
        assert info.total_weeks < 500  # Not unreasonably long

    @pytest.mark.unit
    @pytest.mark.mmm
    @pytest.mark.real_data
    def test_performance_with_real_data(self, mmm_service: MMMService):
        """Test that real data processing performs reasonably."""
        import time
        
        # Time the response curve generation
        start_time = time.time()
        curves = mmm_service.get_response_curves()
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for all channels)
        assert processing_time < 5.0, f"Response curve generation too slow: {processing_time}s"
        
        # Should return data for multiple channels
        assert len(curves["curves"]) >= 3
        
        # Each curve should have enhanced resolution
        for channel, curve_data in curves["curves"].items():
            assert len(curve_data["spend"]) == 100
            assert len(curve_data["response"]) == 100
