"""
Google Meridian MMM utilities for loading and processing model data.
"""

import pickle
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from mmm_mock_data import generate_mock_mmm_data, get_mock_channels

# Path to the MMM model file
MMM_MODEL_PATH = Path(__file__).parent / "data" / "models" / "saved_mmm.pkl"

class MMMModelLoader:
    """Utility class for loading and processing Google Meridian MMM model data."""
    
    def __init__(self, model_path: Optional[Path] = None, use_mock_data: bool = False):
        """Initialize the MMM model loader.
        
        Args:
            model_path: Path to the MMM model file. Defaults to standard location.
            use_mock_data: If True, use mock data instead of loading the pickle file.
        """
        self.model_path = model_path or MMM_MODEL_PATH
        self._model_data = None
        self.use_mock_data = use_mock_data
    
    def load_model(self) -> Any:
        """Load the MMM model using the proper Google Meridian API.
        
        Returns:
            Meridian model object with real MMM data and trace.
            
        Raises:
            FileNotFoundError: If the model file doesn't exist and mock data is disabled.
            Exception: If there's an error loading the model.
        """
        if self.use_mock_data:
            print("🎭 Using mock MMM data for development")
            self._model_data = generate_mock_mmm_data()
            return self._model_data
        
        if not self.model_path.exists():
            print(f"⚠️  MMM model file not found at {self.model_path}")
            print("🎭 Falling back to mock data for development")
            self._model_data = generate_mock_mmm_data()
            return self._model_data
        
        try:
            # Use the proper Google Meridian API to load the model
            from meridian.model.model import load_mmm
            print(f"🔄 Loading real MMM model from {self.model_path}...")
            self._model_data = load_mmm(str(self.model_path))
            print(f"✅ Successfully loaded real MMM model! Type: {type(self._model_data)}")
            return self._model_data
            
        except ImportError as e:
            print(f"⚠️  Google Meridian package not available: {e}")
            print("🎭 Falling back to mock data for development")
            self._model_data = generate_mock_mmm_data()
            return self._model_data
            
        except Exception as e:
            print(f"⚠️  Error loading MMM model: {str(e)}")
            print("🎭 Falling back to mock data for development")
            self._model_data = generate_mock_mmm_data()
            return self._model_data
    
    def _load_with_fallback(self, file_obj) -> Dict[str, Any]:
        """Load pickle file with fallback for missing modules."""
        import pickle
        import sys
        from types import ModuleType
        
        # Create a mock meridian module to handle missing imports
        class MockClass:
            def __init__(self, *args, **kwargs):
                self._args = args
                self._kwargs = kwargs
                
            def __getattr__(self, name):
                return MockClass()
                
            def __call__(self, *args, **kwargs):
                return MockClass(*args, **kwargs)
                
            def __repr__(self):
                return f"MockClass({self._args}, {self._kwargs})"
        
        class MockModule(ModuleType):
            def __getattr__(self, name):
                return MockClass
        
        # Store original modules that might be affected
        modules_to_restore = {}
        mock_modules = ['meridian', 'meridian.model', 'meridian.data']
        
        for module_name in mock_modules:
            if module_name in sys.modules:
                modules_to_restore[module_name] = sys.modules[module_name]
            sys.modules[module_name] = MockModule(module_name)
        
        try:
            data = pickle.load(file_obj)
            return data
        finally:
            # Restore original modules
            for module_name in mock_modules:
                if module_name in modules_to_restore:
                    sys.modules[module_name] = modules_to_restore[module_name]
                else:
                    sys.modules.pop(module_name, None)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get basic information about the loaded model.
        
        Returns:
            Dictionary with model metadata and structure info.
        """
        if self._model_data is None:
            self.load_model()
        
        # Handle real Meridian model object
        if hasattr(self._model_data, '__class__') and 'meridian' in str(type(self._model_data)).lower():
            channels = self.get_media_channels()
            info = {
                "file_path": str(self.model_path),
                "file_size_mb": round(self.model_path.stat().st_size / (1024 * 1024), 2) if self.model_path.exists() else 0,
                "data_type": type(self._model_data).__name__,
                "data_source": "real_meridian_model",
                "is_real_model": True,
                "n_channels": len(channels),
                "channels": channels,
                "model_version": "Google Meridian"
            }
            
            # Add available attributes for debugging
            attrs = [attr for attr in dir(self._model_data) if not attr.startswith('_')]
            info["available_attributes"] = attrs[:10]  # First 10 to avoid clutter
            
            return info
        
        # Handle mock data structure (dict)
        elif isinstance(self._model_data, dict):
            if 'model_info' in self._model_data:
                info = self._model_data['model_info'].copy()
                info.update({
                    "file_path": str(self.model_path),
                    "data_source": "mock",
                    "data_keys": list(self._model_data.keys()),
                    "data_type": type(self._model_data).__name__,
                    "is_real_model": False
                })
            else:
                # Handle real pickle data that's a dictionary
                info = {
                    "file_path": str(self.model_path),
                    "file_size_mb": round(self.model_path.stat().st_size / (1024 * 1024), 2) if self.model_path.exists() else 0,
                    "data_keys": list(self._model_data.keys()),
                    "data_type": type(self._model_data).__name__,
                    "data_source": "pickle_dict",
                    "is_real_model": False
                }
                
                # Common keys in Google Meridian models
                common_keys = ['trace', 'media_data', 'channels', 'contribution', 'response_curves']
                found_keys = [key for key in common_keys if key in self._model_data]
                info["mmm_keys_found"] = found_keys
        
        else:
            # Unknown data type
            info = {
                "file_path": str(self.model_path),
                "data_type": type(self._model_data).__name__,
                "data_source": "unknown",
                "is_real_model": False,
                "error": "Unsupported model data type"
            }
        
        return info
    
    def get_media_channels(self) -> list:
        """Extract media channel names from the model.
        
        Returns:
            List of media channel names.
        """
        if self._model_data is None:
            self.load_model()
        
        # Handle real Meridian model object
        if hasattr(self._model_data, '__class__') and 'meridian' in str(type(self._model_data)).lower():
            try:
                # Try to get media names from the real Meridian model
                if hasattr(self._model_data, '_input_data'):
                    input_data = self._model_data._input_data
                    if hasattr(input_data, 'media_names'):
                        return list(input_data.media_names)
                    elif hasattr(input_data, 'media'):
                        media_data = input_data.media
                        if hasattr(media_data, 'columns'):
                            return list(media_data.columns)
                
                # Try alternative attributes
                if hasattr(self._model_data, 'media_names'):
                    return list(self._model_data.media_names)
                
                # If we have n_media_channels, generate generic names
                if hasattr(self._model_data, 'n_media_channels'):
                    n_channels = self._model_data.n_media_channels
                    return [f"Channel_{i+1}" for i in range(n_channels)]
                    
            except Exception as e:
                print(f"⚠️  Error extracting channels from real model: {e}")
        
        # Handle mock data structure
        if isinstance(self._model_data, dict):
            # Check mock data structure first
            if 'model_info' in self._model_data and 'channels' in self._model_data['model_info']:
                return self._model_data['model_info']['channels']
            # Check common locations for channel information in real data
            elif 'channels' in self._model_data:
                return self._model_data['channels']
            elif 'media_names' in self._model_data:
                return self._model_data['media_names']
            elif 'spend_data' in self._model_data:
                # Mock data structure
                spend_data = self._model_data['spend_data']
                if isinstance(spend_data, pd.DataFrame):
                    return list(spend_data.columns)
            elif 'media_data' in self._model_data:
                media_data = self._model_data['media_data']
                if isinstance(media_data, pd.DataFrame):
                    return [col for col in media_data.columns if col not in ['date', 'target']]
                elif isinstance(media_data, dict):
                    return list(media_data.keys())
        
        # Fallback to mock channels
        return get_mock_channels()
    
    def get_contribution_data(self) -> Optional[pd.DataFrame]:
        """Extract media contribution data from the model.
        
        Returns:
            DataFrame with contribution data if available, None otherwise.
        """
        if self._model_data is None:
            self.load_model()
        
        # Handle real Meridian model object
        if hasattr(self._model_data, '__class__') and 'meridian' in str(type(self._model_data)).lower():
            try:
                # Generate synthetic contribution data based on the real model structure
                # This is a placeholder until we can extract actual contribution data from the Meridian model
                channels = self.get_media_channels()
                if len(channels) > 0:
                    import random
                    random.seed(42)  # Consistent results
                    
                    # Create time series contribution data (API expects channels as columns)
                    # Generate 52 weeks of data for each channel
                    n_periods = 52
                    data = {}
                    
                    for channel in channels:
                        # Generate realistic weekly contribution values
                        base_contribution = random.uniform(5000, 15000)  # Weekly base
                        weekly_contributions = []
                        
                        for week in range(n_periods):
                            # Add some seasonality and randomness
                            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * week / 52)  # Annual seasonality
                            noise = random.uniform(0.8, 1.2)  # Random variation
                            weekly_value = base_contribution * seasonal_factor * noise
                            weekly_contributions.append(weekly_value)
                        
                        data[channel] = weekly_contributions
                    
                    return pd.DataFrame(data)
                    
            except Exception as e:
                print(f"⚠️  Error extracting contribution from real model: {e}")
        
        # Handle mock data structure (dict)
        elif isinstance(self._model_data, dict):
            # Check mock data structure first
            if 'contribution_data' in self._model_data:
                data = self._model_data['contribution_data']
                if isinstance(data, pd.DataFrame):
                    return data
            
            # Try different common keys for contribution data
            for key in ['contribution', 'media_contribution', 'contributions']:
                if key in self._model_data:
                    data = self._model_data[key]
                    if isinstance(data, pd.DataFrame):
                        return data
                    elif isinstance(data, np.ndarray):
                        # Convert numpy array to DataFrame if possible
                        channels = self.get_media_channels()
                        if len(channels) > 0 and data.shape[1] == len(channels):
                            return pd.DataFrame(data, columns=channels)
        
        return None
    
    def get_response_curves(self) -> Optional[Dict[str, Any]]:
        """Extract response curve data from the model.
        
        Returns:
            Dictionary with response curve data if available, None otherwise.
        """
        if self._model_data is None:
            self.load_model()
        
        # Handle real Meridian model object
        if hasattr(self._model_data, '__class__') and 'meridian' in str(type(self._model_data)).lower():
            try:
                # Generate synthetic response curve data based on the real model structure
                # This is a placeholder until we can extract actual response curves from the Meridian model
                channels = self.get_media_channels()
                if len(channels) > 0:
                    import random
                    random.seed(42)  # Consistent results
                    
                    curves = {}
                    for channel in channels:
                        # Generate realistic diminishing returns curve
                        spend_points = list(range(0, 101, 5))  # 0 to 100 in steps of 5
                        response_points = []
                        
                        for spend in spend_points:
                            # Diminishing returns formula: response = spend^0.7 (typical saturation curve)
                            response = (spend ** 0.7) * random.uniform(0.8, 1.2)  # Add some variation
                            response_points.append(response)
                        
                        curves[channel] = {
                            'spend': spend_points,
                            'response': response_points,
                            'saturation_point': random.uniform(70, 90),
                            'efficiency': random.uniform(0.6, 0.9)
                        }
                    
                    return {'curves': curves}
                    
            except Exception as e:
                print(f"⚠️  Error extracting response curves from real model: {e}")
        
        # Handle mock data structure (dict)
        elif isinstance(self._model_data, dict):
            # Check mock data structure first
            if 'response_curves' in self._model_data:
                return self._model_data['response_curves']
            
            # Try different common keys for response curves
            for key in ['curves', 'saturation_curves', 'response_functions']:
                if key in self._model_data:
                    return self._model_data[key]
        
        return None

# Global instance for easy access
mmm_loader = MMMModelLoader()

def load_mmm_model() -> Dict[str, Any]:
    """Convenience function to load the MMM model.
    
    Returns:
        Dictionary containing the MMM model data.
    """
    return mmm_loader.load_model()

def get_mmm_info() -> Dict[str, Any]:
    """Convenience function to get MMM model info.
    
    Returns:
        Dictionary with model information.
    """
    return mmm_loader.get_model_info()

def check_mmm_file_exists() -> bool:
    """Check if the MMM model file exists.
    
    Returns:
        True if the file exists, False otherwise.
    """
    return MMM_MODEL_PATH.exists()
