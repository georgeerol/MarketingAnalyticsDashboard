"""
Mock implementation of MMMServiceProtocol for testing.

This demonstrates how protocols make MMM testing simple without complex model dependencies.
"""

from typing import List, Dict, Any, Optional
from app.services.interfaces import MMMServiceProtocol
from app.schemas.mmm import MMMStatus, MMMModelInfo, MMMChannelSummary


class MockMMMService(MMMServiceProtocol):
    """
    Mock implementation of MMMServiceProtocol.
    
    Provides predictable MMM data for testing without loading actual models.
    """
    
    def __init__(self, simulate_model_loaded: bool = True):
        self.simulate_model_loaded = simulate_model_loaded
        self.channels = ["Google_Search", "Google_Display", "Facebook", "Instagram", "YouTube"]
        self.call_count = {}  # Track method calls for testing
        
        # Mock data
        self.mock_contribution_data = self._generate_mock_contribution_data()
        self.mock_response_curves = self._generate_mock_response_curves()
        self.mock_channel_summary = self._generate_mock_channel_summary()
    
    def _track_call(self, method_name: str):
        """Track method calls for testing verification."""
        self.call_count[method_name] = self.call_count.get(method_name, 0) + 1
    
    def get_model_status(self) -> MMMStatus:
        """Get the status of the MMM model."""
        self._track_call("get_model_status")
        
        return MMMStatus(
            status="loaded" if self.simulate_model_loaded else "not_found",
            message="Model loaded successfully" if self.simulate_model_loaded else "Model file not found",
            file_exists=self.simulate_model_loaded,
            model_info={"last_modified": "2024-01-01T00:00:00Z", "file_size_mb": 25.6} if self.simulate_model_loaded else None
        )
    
    def get_model_info(self) -> MMMModelInfo:
        """Get detailed information about the MMM model."""
        self._track_call("get_model_info")
        
        if not self.simulate_model_loaded:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError("Model not loaded")
        
        return MMMModelInfo(
            model_type="Google Meridian (Mock)",
            version="1.0.0-mock",
            training_period="2023-01-01 to 2023-12-31",
            channels=self.channels,
            data_frequency="weekly",
            total_weeks=52,
            data_source="mock_data"
        )
    
    def get_channel_names(self) -> List[str]:
        """Get list of media channel names from the model."""
        self._track_call("get_channel_names")
        
        if not self.simulate_model_loaded:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError("Model not loaded")
        
        return self.channels.copy()
    
    def get_contribution_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get contribution data for channels from the loaded MMM model."""
        self._track_call("get_contribution_data")
        
        if not self.simulate_model_loaded:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError("Model not loaded")
        
        if channel and channel not in self.channels:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError(f"Channel '{channel}' not found in model")
        
        if channel:
            # Return data for specific channel
            return {
                "channel": channel,
                "data": self.mock_contribution_data["data"][channel],
                "total_contribution": sum(self.mock_contribution_data["data"][channel]),
                "time_periods": len(self.mock_contribution_data["data"][channel])
            }
        
        return self.mock_contribution_data
    
    def get_response_curves(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get response curves for channels from the loaded MMM model."""
        self._track_call("get_response_curves")
        
        if not self.simulate_model_loaded:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError("Model not loaded")
        
        if channel and channel not in self.channels:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError(f"Channel '{channel}' not found in model")
        
        if channel:
            # Return curve for specific channel
            return {
                "channel": channel,
                "curve": self.mock_response_curves["curves"][channel]
            }
        
        return self.mock_response_curves
    
    def get_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """Get summary statistics for all channels."""
        self._track_call("get_channel_summary")
        
        if not self.simulate_model_loaded:
            from app.services.mmm_service import MMMModelError
            raise MMMModelError("Model not loaded")
        
        return self.mock_channel_summary
    
    def _generate_mock_contribution_data(self) -> Dict[str, Any]:
        """Generate mock contribution data."""
        import random
        
        data = {}
        for channel in self.channels:
            # Generate 52 weeks of mock contribution data
            contributions = [random.uniform(1000, 10000) for _ in range(52)]
            data[channel] = contributions
        
        return {
            "data": data,
            "time_periods": 52,
            "channels": self.channels,
            "total_contribution": sum(sum(contributions) for contributions in data.values())
        }
    
    def _generate_mock_response_curves(self) -> Dict[str, Any]:
        """Generate mock response curve data."""
        curves = {}
        
        for channel in self.channels:
            # Generate mock response curve
            spend_points = list(range(0, 100000, 5000))  # Spend from 0 to 100k
            response_points = []
            
            for spend in spend_points:
                # Simple saturation curve: response = spend / (1 + spend/saturation_point)
                saturation_point = 50000
                response = spend / (1 + spend / saturation_point) * 1000
                response_points.append(response)
            
            curves[channel] = {
                "spend": spend_points,
                "response": response_points,
                "saturation_point": saturation_point,
                "efficiency": response_points[-1] / spend_points[-1] if spend_points[-1] > 0 else 0
            }
        
        return {
            "curves": curves,
            "channels": self.channels
        }
    
    def _generate_mock_channel_summary(self) -> Dict[str, MMMChannelSummary]:
        """Generate mock channel summary data."""
        import random
        
        summary = {}
        
        for i, channel in enumerate(self.channels):
            summary[channel] = MMMChannelSummary(
                name=channel,
                total_spend=random.uniform(500000, 1500000),
                total_contribution=random.uniform(50000, 150000),
                efficiency=random.uniform(0.05, 0.15),
                contribution_share=random.uniform(0.15, 0.25),
                avg_weekly_spend=random.uniform(10000, 30000),
                avg_weekly_contribution=random.uniform(1000, 3000)
            )
        
        return summary
    
    # Utility methods for testing
    def set_model_loaded(self, loaded: bool):
        """Set whether the model should simulate being loaded."""
        self.simulate_model_loaded = loaded
    
    def add_channel(self, channel_name: str):
        """Add a channel for testing."""
        if channel_name not in self.channels:
            self.channels.append(channel_name)
            # Update mock data
            self.mock_contribution_data = self._generate_mock_contribution_data()
            self.mock_response_curves = self._generate_mock_response_curves()
            self.mock_channel_summary = self._generate_mock_channel_summary()
    
    def remove_channel(self, channel_name: str):
        """Remove a channel for testing."""
        if channel_name in self.channels:
            self.channels.remove(channel_name)
            # Update mock data
            self.mock_contribution_data = self._generate_mock_contribution_data()
            self.mock_response_curves = self._generate_mock_response_curves()
            self.mock_channel_summary = self._generate_mock_channel_summary()
    
    def get_call_count(self, method_name: str) -> int:
        """Get the number of times a method was called."""
        return self.call_count.get(method_name, 0)
    
    def clear_call_count(self):
        """Clear call count tracking."""
        self.call_count.clear()
    
    def simulate_error(self, method_name: str, error_message: str = "Simulated error"):
        """Configure a method to raise an error (for error testing)."""
        # This could be extended to simulate specific errors for testing
        pass
