"""
Comprehensive tests for Response Curves validation.

This test ensures that all response curves are mathematically correct,
have proper MMM behavior, and provide meaningful business insights.
"""

import pytest
import numpy as np
from app.services.mmm_service import MMMService


class TestResponseCurvesValidation:
    """Test suite for comprehensive response curves validation."""

    @pytest.fixture
    def mmm_service(self):
        """Create MMM service instance."""
        return MMMService()

    @pytest.fixture
    def all_curves(self, mmm_service):
        """Get all response curves for testing."""
        return mmm_service.get_response_curves()

    def test_all_channels_present(self, all_curves):
        """Test that all expected channels are present."""
        expected_channels = ["Channel0", "Channel1", "Channel2", "Channel3", "Channel4"]
        actual_channels = list(all_curves['curves'].keys())
        
        assert len(actual_channels) == 5, f"Expected 5 channels, got {len(actual_channels)}"
        
        for channel in expected_channels:
            assert channel in actual_channels, f"Missing channel: {channel}"

    def test_no_zero_saturation_points(self, all_curves):
        """Test that no channel has a $0 saturation point."""
        for channel, data in all_curves['curves'].items():
            saturation_point = data['saturation_point']
            assert saturation_point > 0, f"{channel} has invalid saturation point: ${saturation_point:,.0f}"
            assert saturation_point > 1000, f"{channel} saturation point too low: ${saturation_point:,.0f}"

    def test_efficiency_ranges(self, all_curves):
        """Test that all efficiency values are in reasonable ranges."""
        for channel, data in all_curves['curves'].items():
            efficiency = data['efficiency']
            assert 0.5 <= efficiency <= 2.0, f"{channel} efficiency {efficiency:.2f} outside reasonable range [0.5, 2.0]"

    def test_monotonic_increasing_response(self, all_curves):
        """Test that all response curves are monotonically increasing."""
        for channel, data in all_curves['curves'].items():
            response = np.array(data['response'])
            
            # Check that response is always increasing (or at least non-decreasing)
            diff = np.diff(response)
            assert np.all(diff >= 0), f"{channel} response curve decreases at some points"
            
            # Check that there's actual growth (not all flat)
            total_growth = response[-1] - response[0]
            assert total_growth > 0, f"{channel} has no response growth"

    def test_diminishing_returns_behavior(self, all_curves):
        """Test that all curves show proper diminishing returns."""
        for channel, data in all_curves['curves'].items():
            spend = np.array(data['spend'])
            response = np.array(data['response'])
            
            # Calculate marginal returns
            marginal_returns = np.diff(response) / np.diff(spend)
            
            # Early returns should be higher than late returns
            early_marginal = np.mean(marginal_returns[:10])
            late_marginal = np.mean(marginal_returns[-10:])
            
            assert early_marginal > late_marginal, f"{channel} doesn't show diminishing returns: early={early_marginal:.6f}, late={late_marginal:.6f}"
            
            # The ratio should be significant (at least 1.2x)
            ratio = early_marginal / late_marginal if late_marginal > 0 else float('inf')
            assert ratio >= 1.2, f"{channel} diminishing returns ratio too low: {ratio:.2f}"

    def test_proper_saturation_curve_shape(self, all_curves):
        """Test that curves have proper saturation shape (steeper at start, flatter at end)."""
        for channel, data in all_curves['curves'].items():
            response = np.array(data['response'])
            
            # Divide curve into quarters and check growth rates
            n = len(response)
            quarter_1 = response[n//4] - response[0]
            quarter_2 = response[n//2] - response[n//4]
            quarter_3 = response[3*n//4] - response[n//2]
            quarter_4 = response[-1] - response[3*n//4]
            
            total_response = response[-1]
            
            # Calculate growth rates as percentage of total
            growth_1 = quarter_1 / total_response
            growth_2 = quarter_2 / total_response
            growth_3 = quarter_3 / total_response
            
            # First quarter should have significant growth
            assert growth_1 > 0.2, f"{channel} first quarter growth too low: {growth_1:.3f}"
            
            # Growth should generally decrease (allowing some flexibility)
            assert growth_1 > growth_3, f"{channel} doesn't show proper saturation shape"

    def test_unique_channel_characteristics(self, all_curves):
        """Test that each channel has unique characteristics."""
        saturation_points = []
        efficiencies = []
        
        for channel, data in all_curves['curves'].items():
            saturation_points.append(data['saturation_point'])
            efficiencies.append(data['efficiency'])
        
        # Check that saturation points are reasonably different
        sat_range = max(saturation_points) - min(saturation_points)
        avg_sat = np.mean(saturation_points)
        assert sat_range > avg_sat * 0.3, "Saturation points too similar across channels"
        
        # Check that efficiencies are reasonably different
        eff_range = max(efficiencies) - min(efficiencies)
        assert eff_range > 0.3, f"Efficiency range too small: {eff_range:.3f}"

    def test_realistic_spend_ranges(self, all_curves):
        """Test that spend ranges are realistic for business use."""
        for channel, data in all_curves['curves'].items():
            spend = np.array(data['spend'])
            
            # Should start at $0
            assert spend[0] == 0, f"{channel} doesn't start at $0 spend"
            
            # Maximum spend should be reasonable (between $50K and $200K)
            max_spend = spend[-1]
            assert 50000 <= max_spend <= 200000, f"{channel} max spend unrealistic: ${max_spend:,.0f}"
            
            # Should have enough data points for smooth curves
            assert len(spend) >= 50, f"{channel} has too few data points: {len(spend)}"

    def test_response_scaling(self, all_curves):
        """Test that response values are properly scaled."""
        for channel, data in all_curves['curves'].items():
            response = np.array(data['response'])
            
            # Response should start at 0
            assert response[0] == 0, f"{channel} response doesn't start at 0"
            
            # Maximum response should be reasonable (not too small or too large)
            max_response = response[-1]
            assert 1000 <= max_response <= 50000, f"{channel} max response unrealistic: {max_response:,.0f}"

    def test_saturation_point_calculation(self, all_curves):
        """Test that saturation points are calculated correctly."""
        for channel, data in all_curves['curves'].items():
            spend = np.array(data['spend'])
            response = np.array(data['response'])
            saturation_point = data['saturation_point']
            
            # Saturation point should be within the spend range
            assert spend[0] <= saturation_point <= spend[-1], f"{channel} saturation point outside spend range"
            
            # Should be reasonable percentage of max spend (20-90%)
            max_spend = spend[-1]
            sat_percentage = saturation_point / max_spend
            assert 0.2 <= sat_percentage <= 0.9, f"{channel} saturation at {sat_percentage:.1%} of max spend"

    def test_data_structure_integrity(self, all_curves):
        """Test that the data structure is correct."""
        assert 'curves' in all_curves, "Missing 'curves' key in response"
        
        for channel, data in all_curves['curves'].items():
            # Check required fields
            required_fields = ['spend', 'response', 'saturation_point', 'efficiency', 'adstock_rate']
            for field in required_fields:
                assert field in data, f"{channel} missing required field: {field}"
            
            # Check data types
            assert isinstance(data['spend'], list), f"{channel} spend should be a list"
            assert isinstance(data['response'], list), f"{channel} response should be a list"
            assert isinstance(data['saturation_point'], (int, float)), f"{channel} saturation_point should be numeric"
            assert isinstance(data['efficiency'], (int, float)), f"{channel} efficiency should be numeric"
            
            # Check array lengths match
            assert len(data['spend']) == len(data['response']), f"{channel} spend and response arrays different lengths"

    def test_business_insights_validity(self, all_curves):
        """Test that the curves provide valid business insights."""
        # Test that we can identify top and bottom performers
        efficiencies = [(channel, data['efficiency']) for channel, data in all_curves['curves'].items()]
        efficiencies.sort(key=lambda x: x[1], reverse=True)
        
        top_performer = efficiencies[0]
        bottom_performer = efficiencies[-1]
        
        # Top performer should have significantly higher efficiency
        efficiency_gap = top_performer[1] - bottom_performer[1]
        assert efficiency_gap > 0.3, f"Efficiency gap too small: {efficiency_gap:.3f}"
        
        # Test that saturation points vary meaningfully
        saturation_points = [data['saturation_point'] for data in all_curves['curves'].values()]
        sat_std = np.std(saturation_points)
        sat_mean = np.mean(saturation_points)
        coefficient_of_variation = sat_std / sat_mean
        assert coefficient_of_variation > 0.15, f"Saturation points too similar: CV={coefficient_of_variation:.3f}"

    @pytest.mark.integration
    def test_end_to_end_curve_generation(self, mmm_service):
        """Test end-to-end curve generation for each channel individually."""
        channels = ["Channel0", "Channel1", "Channel2", "Channel3", "Channel4"]
        
        for channel in channels:
            # Test individual channel curve generation
            single_curve = mmm_service.get_response_curves(channel)
            
            assert channel in single_curve['curves'], f"Channel {channel} not in individual response"
            
            # Should have same structure as bulk generation
            data = single_curve['curves'][channel]
            assert 'saturation_point' in data
            assert 'efficiency' in data
            assert data['saturation_point'] > 0, f"{channel} individual generation has $0 saturation"

    def test_performance_benchmarks(self, all_curves):
        """Test that the curves meet performance expectations."""
        # Channel 4 should be the top performer based on our test data
        channel4_efficiency = all_curves['curves']['Channel4']['efficiency']
        
        # Should be among the top performers
        all_efficiencies = [data['efficiency'] for data in all_curves['curves'].values()]
        max_efficiency = max(all_efficiencies)
        
        # Channel 4 should be close to the top (within 10% of max)
        assert channel4_efficiency >= max_efficiency * 0.9, f"Channel4 efficiency {channel4_efficiency:.2f} not near top {max_efficiency:.2f}"

    def test_mathematical_consistency(self, all_curves):
        """Test mathematical consistency of the curves."""
        for channel, data in all_curves['curves'].items():
            spend = np.array(data['spend'])
            response = np.array(data['response'])
            
            # Test that marginal returns are always positive (most important check)
            marginal_returns = np.diff(response) / np.diff(spend)
            assert np.all(marginal_returns >= 0), f"{channel} has negative marginal returns"
            
            # Test that response starts at 0 and grows
            assert response[0] == 0, f"{channel} response doesn't start at 0"
            assert response[-1] > response[0], f"{channel} response doesn't grow"
            
            # Test that spend increases monotonically
            spend_diff = np.diff(spend)
            assert np.all(spend_diff > 0), f"{channel} spend doesn't increase monotonically"
