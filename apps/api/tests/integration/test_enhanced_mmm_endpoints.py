"""
Integration tests for enhanced MMM API endpoints with real data features.
Tests the new debug endpoint and enhanced response curve functionality.
"""

import pytest
from httpx import AsyncClient


class TestEnhancedMMMEndpoints:
    """Integration tests for enhanced MMM endpoints."""


    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_enhanced_response_curves_structure(self, client: AsyncClient, auth_headers):
        """Test that enhanced response curves have improved structure."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "curves" in data
        curves = data["curves"]
        
        # Should have multiple channels
        assert len(curves) >= 3
        
        for channel, curve_data in curves.items():
            # Verify enhanced structure
            assert "spend" in curve_data
            assert "response" in curve_data
            assert "saturation_point" in curve_data
            assert "efficiency" in curve_data
            assert "adstock_rate" in curve_data
            
            # Verify enhanced resolution (100 points)
            assert len(curve_data["spend"]) == 100
            assert len(curve_data["response"]) == 100
            
            # Verify realistic values
            assert curve_data["efficiency"] > 0
            assert curve_data["saturation_point"] > 100
            assert 0 <= curve_data["adstock_rate"] <= 1

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_efficiency_variation_across_channels(self, client: AsyncClient, auth_headers):
        """Test that channels have different efficiency values (real data working)."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        curves = data["curves"]
        efficiencies = [curve["efficiency"] for curve in curves.values()]
        
        # Should have meaningful variation
        unique_efficiencies = set(round(eff, 3) for eff in efficiencies)
        assert len(unique_efficiencies) > 1, "All channels have same efficiency - real data not working"
        
        # Should have reasonable range
        max_eff = max(efficiencies)
        min_eff = min(efficiencies)
        efficiency_range = max_eff - min_eff
        
        assert efficiency_range > 0.2, f"Efficiency range too small: {efficiency_range}"
        
        # Should have at least one high performer (>1.2) and one lower performer (<1.0)
        high_performers = [eff for eff in efficiencies if eff > 1.2]
        low_performers = [eff for eff in efficiencies if eff < 1.0]
        
        assert len(high_performers) > 0, "No high-performing channels found"
        assert len(low_performers) > 0, "No underperforming channels found"

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_saturation_point_variation(self, client: AsyncClient, auth_headers):
        """Test that saturation points vary meaningfully across channels."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        curves = data["curves"]
        saturation_points = [curve["saturation_point"] for curve in curves.values()]
        
        # Should have variation
        unique_saturations = set(round(sp, 0) for sp in saturation_points)
        assert len(unique_saturations) > 1, "All channels have same saturation point"
        
        # Should be in reasonable ranges
        max_sat = max(saturation_points)
        min_sat = min(saturation_points)
        
        assert min_sat > 500, f"Minimum saturation too low: {min_sat}"
        assert max_sat < 100000, f"Maximum saturation too high: {max_sat}"
        assert max_sat > min_sat * 1.3, "Saturation points not varied enough"

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_adstock_rate_variation(self, client: AsyncClient, auth_headers):
        """Test that adstock rates vary across channels."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        curves = data["curves"]
        adstock_rates = [curve["adstock_rate"] for curve in curves.values()]
        
        # Should have variation
        unique_adstocks = set(round(ar, 3) for ar in adstock_rates)
        assert len(unique_adstocks) > 1, "All channels have same adstock rate"
        
        # Should be in valid range
        for rate in adstock_rates:
            assert 0 <= rate <= 1, f"Invalid adstock rate: {rate}"

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_channel_summary_enhanced_data(self, client: AsyncClient, auth_headers):
        """Test that channel summary includes enhanced efficiency data."""
        response = await client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have multiple channels
        assert len(data) >= 3
        
        efficiencies = []
        for channel, summary in data.items():
            assert "efficiency" in summary
            assert isinstance(summary["efficiency"], (int, float))
            assert summary["efficiency"] > 0
            
            efficiencies.append(summary["efficiency"])
        
        # Efficiency values should vary (real data)
        unique_efficiencies = set(round(eff, 3) for eff in efficiencies)
        assert len(unique_efficiencies) > 1, "Summary efficiencies not varied"

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_consistency_between_endpoints(self, client: AsyncClient, auth_headers):
        """Test consistency between summary and response curves efficiency data."""
        # Get data from both endpoints
        summary_response = await client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        curves_response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert summary_response.status_code == 200
        assert curves_response.status_code == 200
        
        summary_data = summary_response.json()
        curves_data = curves_response.json()
        
        # Should have same channels
        summary_channels = set(summary_data.keys())
        curve_channels = set(curves_data["curves"].keys())
        assert summary_channels == curve_channels
        
        # Efficiency values should be consistent
        for channel in summary_channels:
            summary_eff = summary_data[channel]["efficiency"]
            curve_eff = curves_data["curves"][channel]["efficiency"]
            
            # Should be very close (allowing for floating point differences)
            assert abs(summary_eff - curve_eff) < 0.001, f"Efficiency mismatch for {channel}: {summary_eff} vs {curve_eff}"


class TestRealDataWorkflows:
    """Test complete workflows with real data features."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_complete_enhanced_workflow(self, client: AsyncClient, auth_headers):
        """Test complete workflow using enhanced real data features."""
        # Step 1: Get model info
        info_response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        
        assert info_response.status_code == 200
        
        info_data = info_response.json()
        assert info_data["data_source"] == "real_model"
        
        # Step 3: Get enhanced response curves
        curves_response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        assert curves_response.status_code == 200
        curves_data = curves_response.json()
        
        # Step 4: Get channel summary
        summary_response = await client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        
        # Step 5: Verify real data characteristics
        channels = list(curves_data["curves"].keys())
        assert len(channels) >= 3
        
        # Verify efficiency variation (key indicator of real data)
        efficiencies = [curves_data["curves"][ch]["efficiency"] for ch in channels]
        efficiency_range = max(efficiencies) - min(efficiencies)
        assert efficiency_range > 0.3, "Insufficient efficiency variation for real data"
        
        # Verify enhanced resolution
        for channel in channels:
            curve = curves_data["curves"][channel]
            assert len(curve["spend"]) == 100
            assert len(curve["response"]) == 100

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_performance_with_enhanced_features(self, client: AsyncClient, auth_headers):
        """Test performance of enhanced features."""
        import time
        
        # Time the enhanced response curves endpoint
        start_time = time.time()
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (enhanced features shouldn't be too slow)
        assert processing_time < 3.0, f"Enhanced response curves too slow: {processing_time}s"
        
        # Should return enhanced data
        data = response.json()
        curves = data["curves"]
        
        # Verify enhanced resolution for all channels
        for channel, curve in curves.items():
            assert len(curve["spend"]) == 100
            assert len(curve["response"]) == 100


class TestRealDataErrorHandling:
    """Test error handling with real data features."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_debug_endpoint_error_handling(self, client: AsyncClient, auth_headers):
        """Test debug endpoint handles errors gracefully."""
        # The debug endpoint should handle model loading errors gracefully
        response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "debug_status" in data
            
            if data["debug_status"] == "failed":
                assert "error" in data
                assert isinstance(data["error"], str)

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_enhanced_curves_fallback_behavior(self, client: AsyncClient, auth_headers):
        """Test that enhanced curves fall back gracefully when real parameters unavailable."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should always return valid curves, even if using fallback
        curves = data["curves"]
        assert len(curves) > 0
        
        for channel, curve in curves.items():
            # Should have valid structure regardless of fallback
            assert "efficiency" in curve
            assert "saturation_point" in curve
            assert "adstock_rate" in curve
            
            # Values should be reasonable even in fallback
            assert curve["efficiency"] > 0
            assert curve["saturation_point"] > 0
            assert 0 <= curve["adstock_rate"] <= 1


class TestRealDataValidation:
    """Test validation of real data vs mock data."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.real_data
    @pytest.mark.asyncio
    async def test_real_data_indicators(self, client: AsyncClient, auth_headers):
        """Test that we can detect real vs mock data through API."""
        # Get model info
        info_response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        assert info_response.status_code == 200
        info_data = info_response.json()
        
        # Should indicate real data
        assert info_data["data_source"] == "real_model"
        assert info_data["model_type"] == "Google Meridian"
        
        # Get response curves
        curves_response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        assert curves_response.status_code == 200
        curves_data = curves_response.json()
        
        # Real data indicators:
        # 1. Efficiency values should vary significantly
        efficiencies = [curve["efficiency"] for curve in curves_data["curves"].values()]
        efficiency_std = (sum((x - sum(efficiencies)/len(efficiencies))**2 for x in efficiencies) / len(efficiencies))**0.5
        assert efficiency_std > 0.1, "Efficiency values too uniform for real data"
        
        # 2. Should have realistic saturation points (not round numbers)
        saturation_points = [curve["saturation_point"] for curve in curves_data["curves"].values()]
        round_saturations = [sp for sp in saturation_points if sp % 1000 == 0]
        assert len(round_saturations) < len(saturation_points), "Too many round saturation points for real data"
        
        # 3. Adstock rates should vary
        adstock_rates = [curve["adstock_rate"] for curve in curves_data["curves"].values()]
        unique_adstocks = set(round(ar, 3) for ar in adstock_rates)
        assert len(unique_adstocks) > 1, "Adstock rates too uniform for real data"
