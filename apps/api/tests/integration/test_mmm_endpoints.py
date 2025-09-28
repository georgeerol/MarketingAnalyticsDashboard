"""
Integration tests for MMM API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestMMMEndpoints:
    """Integration tests for MMM endpoints."""


    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_info_authenticated(self, client: AsyncClient, auth_headers):
        """Test MMM info endpoint with authentication."""
        response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_type" in data
        assert "version" in data
        assert "training_period" in data
        assert "channels" in data
        assert "data_frequency" in data
        assert "total_weeks" in data
        assert "data_source" in data
        
        assert isinstance(data["channels"], list)
        assert len(data["channels"]) > 0

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_mmm_info_unauthenticated(self, client: AsyncClient):
        """Test MMM info endpoint without authentication."""
        response = await client.get("/api/v1/mmm/info")
        
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_channels_authenticated(self, client: AsyncClient, auth_headers):
        """Test get channels endpoint with authentication."""
        response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "channels" in data
        assert "count" in data
        assert "message" in data
        
        assert isinstance(data["channels"], list)
        assert len(data["channels"]) > 0
        assert data["count"] == len(data["channels"])

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_channels_unauthenticated(self, client: AsyncClient):
        """Test get channels endpoint without authentication."""
        response = await client.get("/api/v1/mmm/channels")
        
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_contribution_all_channels(self, client: AsyncClient, auth_headers):
        """Test get contribution data for all channels."""
        response = await client.get("/api/v1/mmm/contribution", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "channels" in data
        assert "data" in data
        assert "summary" in data
        assert "shape" in data
        
        assert isinstance(data["channels"], list)
        assert isinstance(data["data"], dict)
        assert len(data["channels"]) > 0

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_contribution_specific_channel(self, client: AsyncClient, auth_headers):
        """Test get contribution data for specific channel."""
        # First get available channels
        channels_response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
        channels_data = channels_response.json()
        
        if channels_data["channels"]:
            channel = channels_data["channels"][0]
            
            response = await client.get(f"/api/v1/mmm/contribution?channel={channel}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "channels" in data
            assert "data" in data
            assert "summary" in data
            assert channel in data["channels"] or len(data["channels"]) == 1


    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_contribution_unauthenticated(self, client: AsyncClient):
        """Test get contribution data without authentication."""
        response = await client.get("/api/v1/mmm/contribution")
        
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_response_curves_all_channels(self, client: AsyncClient, auth_headers):
        """Test get response curves for all channels."""
        response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "curves" in data
        assert isinstance(data["curves"], dict)
        assert len(data["curves"]) > 0
        
        # Check structure of curve data
        for channel, curve in data["curves"].items():
            assert "spend" in curve
            assert "response" in curve
            assert "saturation_point" in curve
            assert "efficiency" in curve
            assert "adstock_rate" in curve
            
            assert isinstance(curve["spend"], list)
            assert isinstance(curve["response"], list)
            assert len(curve["spend"]) == len(curve["response"])

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_response_curves_specific_channel(self, client: AsyncClient, auth_headers):
        """Test get response curves for specific channel."""
        # First get available channels
        channels_response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
        channels_data = channels_response.json()
        
        if channels_data["channels"]:
            channel = channels_data["channels"][0]
            
            response = await client.get(f"/api/v1/mmm/response-curves?channel={channel}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "curves" in data
            assert isinstance(data["curves"], dict)
            assert channel in data["curves"] or len(data["curves"]) == 1


    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_response_curves_unauthenticated(self, client: AsyncClient):
        """Test get response curves without authentication."""
        response = await client.get("/api/v1/mmm/response-curves")
        
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_channel_summary_authenticated(self, client: AsyncClient, auth_headers):
        """Test get channel summary with authentication."""
        response = await client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of summary data
        for channel, summary in data.items():
            assert "name" in summary
            assert "total_spend" in summary
            assert "total_contribution" in summary
            assert "contribution_share" in summary
            assert "efficiency" in summary
            assert "avg_weekly_spend" in summary
            assert "avg_weekly_contribution" in summary

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_get_channel_summary_unauthenticated(self, client: AsyncClient):
        """Test get channel summary without authentication."""
        response = await client.get("/api/v1/mmm/channels/summary")
        
        assert response.status_code == 401


class TestMMMWorkflow:
    """Test complete MMM data access workflows."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_complete_mmm_workflow(self, client: AsyncClient, auth_headers):
        """Test complete MMM data access workflow."""
        # Step 1: Get MMM info
        info_response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        assert info_response.status_code == 200
        info_data = info_response.json()
        
        # Step 2: Get model info
        info_response = await client.get("/api/v1/mmm/info", headers=auth_headers)
        assert info_response.status_code == 200
        info_data = info_response.json()
        
        # Step 3: Get available channels
        channels_response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
        assert channels_response.status_code == 200
        channels_data = channels_response.json()
        
        channels = channels_data["channels"]
        assert len(channels) > 0
        
        # Step 4: Get contribution data for all channels
        contribution_response = await client.get("/api/v1/mmm/contribution", headers=auth_headers)
        assert contribution_response.status_code == 200
        contribution_data = contribution_response.json()
        
        # Step 5: Get response curves for all channels
        curves_response = await client.get("/api/v1/mmm/response-curves", headers=auth_headers)
        assert curves_response.status_code == 200
        curves_data = curves_response.json()
        
        # Step 6: Get channel summary
        summary_response = await client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        
        # Verify data consistency
        assert len(contribution_data["channels"]) == len(channels)
        assert len(curves_data["curves"]) == len(channels)
        assert len(summary_data) == len(channels)

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_channel_specific_workflow(self, client: AsyncClient, auth_headers):
        """Test workflow for getting data for specific channels."""
        # Get available channels
        channels_response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
        channels_data = channels_response.json()
        
        if channels_data["channels"]:
            channel = channels_data["channels"][0]
            
            # Get contribution data for specific channel
            contribution_response = await client.get(
                f"/api/v1/mmm/contribution?channel={channel}", 
                headers=auth_headers
            )
            assert contribution_response.status_code == 200
            contribution_data = contribution_response.json()
            
            # Get response curves for specific channel
            curves_response = await client.get(
                f"/api/v1/mmm/response-curves?channel={channel}", 
                headers=auth_headers
            )
            assert curves_response.status_code == 200
            curves_data = curves_response.json()
            
            # Verify channel-specific data
            assert channel in contribution_data["channels"] or len(contribution_data["channels"]) == 1
            assert channel in curves_data["curves"] or len(curves_data["curves"]) == 1


class TestMMMErrorHandling:
    """Test MMM endpoint error handling."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_invalid_token_format(self, client: AsyncClient):
        """Test MMM endpoints with invalid token format."""
        headers = {"Authorization": "InvalidTokenFormat"}
        
        response = await client.get("/api/v1/mmm/info", headers=headers)
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_expired_token(self, client: AsyncClient, test_user):
        """Test MMM endpoints with expired token."""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/v1/mmm/info", headers=headers)
        
        assert response.status_code == 401



class TestMMMPerformance:
    """Test MMM endpoint performance characteristics."""

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient, auth_headers):
        """Test multiple concurrent requests to MMM endpoints."""
        import asyncio
        
        # Create multiple concurrent requests
        tasks = [
            client.get("/api/v1/mmm/info", headers=auth_headers),
            client.get("/api/v1/mmm/channels", headers=auth_headers),
            client.get("/api/v1/mmm/info", headers=auth_headers),
            client.get("/api/v1/mmm/channels/summary", headers=auth_headers)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.mmm
    @pytest.mark.asyncio
    async def test_repeated_requests_caching(self, client: AsyncClient, auth_headers):
        """Test that repeated requests are handled efficiently (caching)."""
        # Make the same request multiple times
        for _ in range(5):
            response = await client.get("/api/v1/mmm/channels", headers=auth_headers)
            assert response.status_code == 200
            
            # Response should be consistent
            data = response.json()
            assert "channels" in data
            assert len(data["channels"]) > 0