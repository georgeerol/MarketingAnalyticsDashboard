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
    
    def load_model(self) -> Dict[str, Any]:
        """Load the MMM model from pickle file or use mock data.
        
        Returns:
            Dictionary containing the MMM model data and trace.
            
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
            # Try to load with custom unpickler that handles missing modules
            with open(self.model_path, 'rb') as f:
                try:
                    self._model_data = pickle.load(f)
                    print(f"✅ Successfully loaded MMM model from {self.model_path}")
                    return self._model_data
                except ModuleNotFoundError as e:
                    if 'meridian' in str(e):
                        print(f"⚠️  Missing Meridian package: {e}")
                        print("🎭 Falling back to mock data for development")
                        self._model_data = generate_mock_mmm_data()
                        return self._model_data
                    else:
                        raise e
            
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
        
        # Handle mock data structure
        if 'model_info' in self._model_data:
            info = self._model_data['model_info'].copy()
            info.update({
                "file_path": str(self.model_path),
                "data_source": "mock",
                "data_keys": list(self._model_data.keys()),
                "data_type": type(self._model_data).__name__,
            })
        else:
            # Handle real pickle data
            info = {
                "file_path": str(self.model_path),
                "file_size_mb": round(self.model_path.stat().st_size / (1024 * 1024), 2) if self.model_path.exists() else 0,
                "data_keys": list(self._model_data.keys()) if isinstance(self._model_data, dict) else "Not a dictionary",
                "data_type": type(self._model_data).__name__,
                "data_source": "pickle"
            }
        
        # Try to extract more specific info if it's a standard MMM structure
        if isinstance(self._model_data, dict):
            # Common keys in Google Meridian models
            common_keys = ['trace', 'media_data', 'channels', 'contribution', 'response_curves']
            found_keys = [key for key in common_keys if key in self._model_data]
            info["mmm_keys_found"] = found_keys
        
        return info
    
    def get_media_channels(self) -> list:
        """Extract media channel names from the model.
        
        Returns:
            List of media channel names.
        """
        if self._model_data is None:
            self.load_model()
        
        # Try different common structures for channel names
        channels = []
        
        if isinstance(self._model_data, dict):
            # Check mock data structure first
            if 'model_info' in self._model_data and 'channels' in self._model_data['model_info']:
                channels = self._model_data['model_info']['channels']
            # Check common locations for channel information in real data
            elif 'channels' in self._model_data:
                channels = self._model_data['channels']
            elif 'media_names' in self._model_data:
                channels = self._model_data['media_names']
            elif 'spend_data' in self._model_data:
                # Mock data structure
                spend_data = self._model_data['spend_data']
                if isinstance(spend_data, pd.DataFrame):
                    channels = list(spend_data.columns)
            elif 'media_data' in self._model_data:
                media_data = self._model_data['media_data']
                if isinstance(media_data, pd.DataFrame):
                    channels = [col for col in media_data.columns if col not in ['date', 'target']]
                elif isinstance(media_data, dict):
                    channels = list(media_data.keys())
        
        return channels
    
    def get_contribution_data(self) -> Optional[pd.DataFrame]:
        """Extract media contribution data from the model.
        
        Returns:
            DataFrame with contribution data if available, None otherwise.
        """
        if self._model_data is None:
            self.load_model()
        
        if isinstance(self._model_data, dict):
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
        
        if isinstance(self._model_data, dict):
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
