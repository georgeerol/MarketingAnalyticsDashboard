#!/usr/bin/env python3
"""
Test loading the real saved_mmm.pkl file using the proper Google Meridian API.
"""

from pathlib import Path
import sys

def test_meridian_load():
    """Test loading the MMM model using the proper Meridian API."""
    
    # Path to your model file
    model_path = Path(__file__).parent / "data" / "models" / "saved_mmm.pkl"
    
    if not model_path.exists():
        print(f"❌ Model file not found at: {model_path}")
        return None
    
    print(f"📁 Found model file at: {model_path}")
    print(f"📊 File size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # Import the proper Meridian API
        from meridian.model.model import load_mmm
        print("✅ Meridian package imported successfully!")
        
        # Load your real model trace - this is the correct way!
        print(f"\n🔄 Loading MMM model from {model_path}...")
        model_trace = load_mmm(str(model_path))
        
        print("🎉 SUCCESS! Real MMM model loaded!")
        print(f"📋 Model type: {type(model_trace)}")
        
        # Analyze the real model structure
        analyze_real_model(model_trace)
        
        return model_trace
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def analyze_real_model(model_trace):
    """Analyze the structure of the real MMM model."""
    
    print(f"\n📊 REAL MMM MODEL ANALYSIS:")
    print(f"  Type: {type(model_trace)}")
    
    # Check for common Meridian model attributes
    if hasattr(model_trace, '__dict__'):
        attrs = list(model_trace.__dict__.keys())
        print(f"  Attributes ({len(attrs)}): {attrs[:10]}...")  # Show first 10
        
        # Look for key MMM data
        key_attrs = ['media_names', 'geo_names', 'time_periods', 'n_media_channels', 
                    'media_spend', 'revenue', 'contribution', 'adstock_params', 
                    'saturation_params', 'media_effect']
        
        found_attrs = []
        for attr in key_attrs:
            if hasattr(model_trace, attr):
                try:
                    value = getattr(model_trace, attr)
                    found_attrs.append(attr)
                    print(f"    ✅ {attr}: {type(value)}")
                    
                    # Show details for key attributes
                    if attr == 'media_names' and hasattr(value, '__len__'):
                        print(f"       📺 Media channels: {list(value)}")
                    elif attr == 'n_media_channels':
                        print(f"       📊 Number of channels: {value}")
                    elif hasattr(value, 'shape'):
                        print(f"       📐 Shape: {value.shape}")
                    elif hasattr(value, '__len__') and not isinstance(value, str):
                        print(f"       📏 Length: {len(value)}")
                        
                except Exception as e:
                    print(f"    ⚠️  {attr}: Error accessing ({e})")
        
        print(f"\n🎯 Found {len(found_attrs)} key MMM attributes: {found_attrs}")
        
        # Try to extract contribution data
        if hasattr(model_trace, 'contribution'):
            try:
                contribution = getattr(model_trace, 'contribution')
                print(f"\n💰 CONTRIBUTION DATA:")
                print(f"    Type: {type(contribution)}")
                if hasattr(contribution, 'shape'):
                    print(f"    Shape: {contribution.shape}")
                if hasattr(contribution, 'sum'):
                    total = contribution.sum()
                    print(f"    Total contribution: {total}")
            except Exception as e:
                print(f"    ⚠️  Error analyzing contribution: {e}")
    
    else:
        print(f"  No __dict__ attribute found")

if __name__ == "__main__":
    model_trace = test_meridian_load()
    if model_trace:
        print(f"\n🎉 SUCCESS! Your real MMM model is now accessible!")
        print(f"   Use: from meridian.model.model import load_mmm")
        print(f"   Then: model_trace = load_mmm('saved_mmm.pkl')")
    else:
        print(f"\n❌ Failed to load the real MMM model")
