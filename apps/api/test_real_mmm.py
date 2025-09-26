#!/usr/bin/env python3
"""
Test script to explore and load the real saved_mmm.pkl file.
"""

import pickle
import sys
from pathlib import Path
from typing import Any, Dict

def explore_pickle_file():
    """Explore the structure of the saved_mmm.pkl file."""
    
    model_path = Path(__file__).parent / "data" / "models" / "saved_mmm.pkl"
    
    if not model_path.exists():
        print(f"❌ Model file not found at: {model_path}")
        return None
    
    print(f"📁 Found model file at: {model_path}")
    print(f"📊 File size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Check if Google Meridian is available
    try:
        import meridian
        print("✅ Google Meridian package is available")
        meridian_available = True
    except ImportError:
        print("⚠️  Google Meridian package not found")
        print("💡 Install with: uv add google-meridian")
        meridian_available = False
    
    # Try different loading approaches
    print("\n🔍 Attempting to load pickle file...")
    
    # Method 1: Direct loading (if Meridian is available)
    if meridian_available:
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                print("✅ Successfully loaded with Meridian!")
                analyze_data_structure(data)
                return data
        except Exception as e:
            print(f"❌ Direct loading failed: {e}")
    
    # Method 2: Custom unpickler for missing modules
    try:
        data = load_with_custom_unpickler(model_path)
        if data:
            print("✅ Successfully loaded with custom unpickler!")
            analyze_data_structure(data)
            return data
    except Exception as e:
        print(f"❌ Custom unpickler failed: {e}")
    
    return None

def load_with_custom_unpickler(model_path: Path) -> Any:
    """Load pickle file with custom unpickler that handles missing modules."""
    import sys
    import types
    
    # Create mock modules
    mock_modules = {}
    
    def create_mock_module(module_name):
        if module_name in mock_modules:
            return mock_modules[module_name]
        
        # Create a mock module
        mock_module = types.ModuleType(module_name)
        mock_modules[module_name] = mock_module
        sys.modules[module_name] = mock_module
        return mock_module
    
    def create_mock_class(module_name, class_name):
        # Create mock module if it doesn't exist
        mock_module = create_mock_module(module_name)
        
        # Create a mock class that can hold attributes
        class MockClass:
            def __init__(self, *args, **kwargs):
                # Store all arguments as attributes
                for i, arg in enumerate(args):
                    setattr(self, f'_arg_{i}', arg)
                self.__dict__.update(kwargs)
            
            def __repr__(self):
                return f"Mock{class_name}({len(self.__dict__)} attributes)"
            
            def __getstate__(self):
                return self.__dict__
            
            def __setstate__(self, state):
                self.__dict__.update(state)
        
        MockClass.__name__ = class_name
        MockClass.__module__ = module_name
        MockClass.__qualname__ = class_name
        
        # Add the class to the mock module
        setattr(mock_module, class_name, MockClass)
        
        return MockClass
    
    # Pre-create known Meridian classes
    create_mock_class('meridian.model.model', 'Meridian')
    create_mock_class('meridian.data.input_data', 'InputData')
    
    class MeridianUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Handle missing meridian modules
            if module.startswith('meridian') or 'meridian' in module:
                print(f"🎭 Creating mock for {module}.{name}")
                return create_mock_class(module, name)
            
            # Handle other missing modules
            try:
                return super().find_class(module, name)
            except (ImportError, AttributeError, ModuleNotFoundError):
                print(f"🎭 Creating mock for {module}.{name}")
                return create_mock_class(module, name)
    
    try:
        with open(model_path, 'rb') as f:
            unpickler = MeridianUnpickler(f)
            return unpickler.load()
    finally:
        # Clean up mock modules from sys.modules
        for module_name in list(mock_modules.keys()):
            if module_name in sys.modules:
                del sys.modules[module_name]

def analyze_data_structure(data: Any) -> None:
    """Analyze the structure of the loaded MMM data."""
    
    print(f"\n📋 Data Analysis:")
    print(f"  Type: {type(data)}")
    
    if hasattr(data, '__dict__'):
        attrs = list(data.__dict__.keys())
        print(f"  Attributes: {attrs}")
        
        # Analyze key attributes
        for attr in attrs[:10]:  # Show first 10 attributes
            try:
                value = getattr(data, attr)
                print(f"    - {attr}: {type(value)}")
                if hasattr(value, 'shape'):
                    print(f"      Shape: {value.shape}")
                elif hasattr(value, '__len__') and not isinstance(value, str):
                    try:
                        print(f"      Length: {len(value)}")
                    except:
                        pass
            except Exception as e:
                print(f"    - {attr}: Error accessing ({e})")
    
    elif isinstance(data, dict):
        keys = list(data.keys())
        print(f"  Dictionary keys: {keys}")
        
        # Analyze key values
        for key in keys[:10]:  # Show first 10 keys
            try:
                value = data[key]
                print(f"    - {key}: {type(value)}")
                if hasattr(value, 'shape'):
                    print(f"      Shape: {value.shape}")
                elif hasattr(value, '__len__') and not isinstance(value, str):
                    try:
                        print(f"      Length: {len(value)}")
                    except:
                        pass
            except Exception as e:
                print(f"    - {key}: Error accessing ({e})")
    
    elif hasattr(data, '__len__'):
        try:
            print(f"  Length: {len(data)}")
        except:
            pass

def extract_mmm_insights(data: Any) -> Dict[str, Any]:
    """Extract key insights from the MMM model data."""
    
    insights = {
        "channels": [],
        "time_periods": None,
        "contributions": {},
        "model_info": {}
    }
    
    try:
        # Try to extract channel information
        if hasattr(data, 'media_names') or (isinstance(data, dict) and 'media_names' in data):
            channels = getattr(data, 'media_names', data.get('media_names', []))
            insights["channels"] = channels
            print(f"📊 Found {len(channels)} media channels: {channels}")
        
        # Try to extract time information
        if hasattr(data, 'n_time_periods') or (isinstance(data, dict) and 'n_time_periods' in data):
            time_periods = getattr(data, 'n_time_periods', data.get('n_time_periods'))
            insights["time_periods"] = time_periods
            print(f"📅 Time periods: {time_periods}")
        
        # Try to extract contribution data
        if hasattr(data, 'contribution') or (isinstance(data, dict) and 'contribution' in data):
            contribution = getattr(data, 'contribution', data.get('contribution'))
            if contribution is not None:
                print(f"💰 Found contribution data: {type(contribution)}")
                if hasattr(contribution, 'shape'):
                    print(f"    Shape: {contribution.shape}")
        
        # Look for other common MMM attributes
        common_attrs = ['media_spend', 'target', 'media_effect', 'baseline', 'adstock_params']
        for attr in common_attrs:
            if hasattr(data, attr) or (isinstance(data, dict) and attr in data):
                value = getattr(data, attr, data.get(attr))
                print(f"📈 Found {attr}: {type(value)}")
                if hasattr(value, 'shape'):
                    print(f"    Shape: {value.shape}")
        
    except Exception as e:
        print(f"⚠️  Error extracting insights: {e}")
    
    return insights

if __name__ == "__main__":
    print("🚀 Testing Real MMM Model Loading")
    print("=" * 60)
    
    # Explore and load the pickle file
    data = explore_pickle_file()
    
    if data is not None:
        print("\n" + "=" * 60)
        print("🔍 Extracting MMM Insights...")
        insights = extract_mmm_insights(data)
        
        print(f"\n📋 Summary:")
        print(f"  - Channels: {len(insights['channels'])}")
        print(f"  - Time periods: {insights['time_periods']}")
        print(f"  - Data structure: {type(data)}")
    else:
        print("\n❌ Could not load the MMM model data")
        print("💡 Suggestions:")
        print("   1. Install Google Meridian: uv add google-meridian")
        print("   2. Check if the pickle file is valid")
        print("   3. Verify the file path is correct")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
