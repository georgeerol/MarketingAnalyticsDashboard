"""
Integration tests for MMM API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock

from mmm_utils import MMMModelLoader


class TestMMMEndpoints:
    """Integration tests for MMM API endpoints."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_status_unauthorized(self, client: AsyncClient):
        """Test MMM status endpoint without authentication."""
        response = await client.get("/mmm/status")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_status_authorized(self, client: AsyncClient, auth_headers: dict):
        """Test MMM status endpoint with authentication."""
        response = await client.get("/mmm/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "file_exists" in data
        assert "model_info" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_info_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM info endpoint."""
        response = await client.get("/mmm/info", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "file_path" in data
        assert "data_source" in data
        assert "is_real_model" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_channels_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM channels endpoint."""
        response = await client.get("/mmm/channels", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "channels" in data
        assert "count" in data
        assert "message" in data
        assert isinstance(data["channels"], list)
        assert data["count"] == len(data["channels"])

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_contribution_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM contribution endpoint."""
        response = await client.get("/mmm/contribution", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "channels" in data
        assert "data" in data
        assert "summary" in data
        assert isinstance(data["channels"], list)
        assert isinstance(data["data"], list)

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_contribution_specific_channel(self, client: AsyncClient, auth_headers: dict):
        """Test MMM contribution endpoint for specific channel."""
        # First get available channels
        channels_response = await client.get("/mmm/channels", headers=auth_headers)
        channels = channels_response.json()["channels"]
        
        if channels:
            test_channel = channels[0]
            response = await client.get(f"/mmm/contribution?channel={test_channel}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "channel" in data
            assert data["channel"] == test_channel
            assert "data" in data
            assert "summary" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_response_curves_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM response curves endpoint."""
        response = await client.get("/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "curves" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_response_curves_specific_channel(self, client: AsyncClient, auth_headers: dict):
        """Test MMM response curves endpoint for specific channel."""
        # First get available channels
        channels_response = await client.get("/mmm/channels", headers=auth_headers)
        channels = channels_response.json()["channels"]
        
        if channels:
            test_channel = channels[0]
            response = await client.get(f"/mmm/response-curves?channel={test_channel}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "curves" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_explore_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM explore endpoint."""
        response = await client.get("/mmm/explore", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_structure" in data
        assert "available_data" in data

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_test_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test MMM test endpoint."""
        response = await client.get("/mmm/test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "tests" in data


class TestMMMEndpointsWithRealModel:
    """Integration tests with real MMM model data."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_model_loading_integration(self, client: AsyncClient, auth_headers: dict):
        """Test integration with real MMM model if available."""
        # Test if real model can be loaded
        response = await client.get("/mmm/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        if data.get("file_exists"):
            # Real model file exists, test real data endpoints
            info_response = await client.get("/mmm/info", headers=auth_headers)
            info_data = info_response.json()
            
            if info_data.get("is_real_model"):
                # Test that we get real data
                channels_response = await client.get("/mmm/channels", headers=auth_headers)
                channels_data = channels_response.json()
                
                # Real model should have 5 channels
                assert channels_data["count"] == 5
                assert all(channel.startswith("Channel_") for channel in channels_data["channels"])

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mock_data_fallback(self, client: AsyncClient, auth_headers: dict):
        """Test that mock data fallback works when real model unavailable."""
        with patch('mmm_utils.MMMModelLoader') as mock_loader_class:
            # Mock the loader to always use mock data
            mock_loader = Mock()
            mock_loader.get_model_info.return_value = {
                "data_source": "mock",
                "is_real_model": False,
                "file_path": "/fake/path",
                "file_size_mb": 0
            }
            mock_loader.get_media_channels.return_value = ["Channel_1", "Channel_2", "Channel_3"]
            mock_loader_class.return_value = mock_loader
            
            response = await client.get("/mmm/channels", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3


class TestMMMEndpointErrors:
    """Test error handling in MMM endpoints."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_contribution_invalid_channel(self, client: AsyncClient, auth_headers: dict):
        """Test MMM contribution endpoint with invalid channel."""
        response = await client.get("/mmm/contribution?channel=NonExistentChannel", headers=auth_headers)
        
        # Should still return 200 but with empty/default data
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_endpoints_with_model_error(self, client: AsyncClient, auth_headers: dict):
        """Test MMM endpoints when model loading fails."""
        with patch('mmm_utils.MMMModelLoader.load_model', side_effect=Exception("Model loading failed")):
            response = await client.get("/mmm/status", headers=auth_headers)
            
            # Should handle error gracefully
            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_endpoints_with_missing_file(self, client: AsyncClient, auth_headers: dict):
        """Test MMM endpoints when model file is missing."""
        with patch('mmm_utils.MMM_MODEL_PATH') as mock_path:
            mock_path.exists.return_value = False
            
            response = await client.get("/mmm/status", headers=auth_headers)
            
            # Should fallback to mock data
            assert response.status_code == 200


class TestMMMEndpointPerformance:
    """Test performance of MMM endpoints."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_mmm_endpoints_response_time(self, client: AsyncClient, auth_headers: dict):
        """Test that MMM endpoints respond within reasonable time."""
        import time
        
        endpoints = [
            "/mmm/status",
            "/mmm/info", 
            "/mmm/channels",
            "/mmm/contribution",
            "/mmm/response-curves"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = await client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_concurrent_requests(self, client: AsyncClient, auth_headers: dict):
        """Test MMM endpoints handle concurrent requests."""
        import asyncio
        
        async def make_request(endpoint):
            return await client.get(endpoint, headers=auth_headers)
        
        # Make concurrent requests to different endpoints
        tasks = [
            make_request("/mmm/status"),
            make_request("/mmm/channels"),
            make_request("/mmm/contribution"),
            make_request("/mmm/info")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
