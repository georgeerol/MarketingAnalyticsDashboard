#!/usr/bin/env python3
"""
MMM Model Inspector Script

This script loads and displays the Google Meridian MMM model data,
showing structure, parameters, and key insights in a readable format.

Usage:
    python scripts/inspect_model.py [--output-file path/to/output.txt] [--format json|text]
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
import xarray as xr
from app.services.mmm_service import MMMService


def format_array_info(arr, name="Array"):
    """Format array information in a readable way."""
    if isinstance(arr, np.ndarray):
        return f"{name}: shape={arr.shape}, dtype={arr.dtype}, min={arr.min():.4f}, max={arr.max():.4f}, mean={arr.mean():.4f}"
    elif isinstance(arr, xr.DataArray):
        return f"{name}: dims={arr.dims}, shape={arr.shape}, dtype={arr.dtype}"
    else:
        return f"{name}: type={type(arr)}, value={arr}"


def inspect_model_structure(model_data):
    """Inspect and return the structure of the model data."""
    info = {
        "model_type": str(type(model_data)),
        "structure": {},
        "summary": {}
    }
    
    if hasattr(model_data, 'posterior'):
        posterior = model_data.posterior
        info["structure"]["posterior"] = {
            "type": str(type(posterior)),
            "dims": dict(posterior.dims) if hasattr(posterior, 'dims') else "No dims",
            "coords": list(posterior.coords.keys()) if hasattr(posterior, 'coords') else "No coords",
            "data_vars": list(posterior.data_vars.keys()) if hasattr(posterior, 'data_vars') else "No data_vars"
        }
        
        # Analyze key variables
        if hasattr(posterior, 'data_vars'):
            for var_name in posterior.data_vars:
                var_data = posterior[var_name]
                info["structure"][f"posterior.{var_name}"] = {
                    "dims": var_data.dims,
                    "shape": var_data.shape,
                    "dtype": str(var_data.dtype)
                }
    
    return info


def get_channel_insights(mmm_service):
    """Get insights for each channel."""
    try:
        channels = mmm_service.get_channel_names()
        insights = {}
        
        for channel in channels:
            try:
                # Get response curves
                curves = mmm_service.get_response_curves(channel)
                if channel in curves.get('curves', {}):
                    curve_data = curves['curves'][channel]
                    insights[channel] = {
                        "saturation_point": f"${curve_data.get('saturation_point', 0):,.0f}",
                        "efficiency": f"{curve_data.get('efficiency', 0):.3f}",
                        "adstock_rate": f"{curve_data.get('adstock_rate', 0):.3f}",
                        "max_spend": f"${max(curve_data.get('spend', [0])):,.0f}",
                        "max_response": f"{max(curve_data.get('response', [0])):,.0f}"
                    }
            except Exception as e:
                insights[channel] = {"error": str(e)}
        
        return insights
    except Exception as e:
        return {"error": str(e)}


def get_contribution_summary(mmm_service):
    """Get contribution data summary."""
    try:
        contributions = mmm_service.get_contribution_data()
        periods = contributions.get('periods', [])
        summary = {
            "total_periods": len(periods),
            "channels": {},
            "date_range": ""
        }
        
        # Add date range if periods exist
        if periods:
            summary["date_range"] = f"{periods[0]} to {periods[-1]}"
        
        for channel, data in contributions.get('contributions', {}).items():
            if data:
                values = [d['value'] for d in data if 'value' in d]
                if values:
                    summary["channels"][channel] = {
                        "total_contribution": f"{sum(values):,.0f}",
                        "avg_contribution": f"{np.mean(values):,.0f}",
                        "max_contribution": f"{max(values):,.0f}",
                        "min_contribution": f"{min(values):,.0f}",
                        "data_points": len(values)
                    }
        
        # If no channel data, add a note
        if not summary["channels"]:
            summary["note"] = "No contribution data available - this is normal for raw model inspection"
        
        return summary
    except Exception as e:
        return {"error": str(e)}


def format_text_output(model_info, channel_insights, contribution_summary, mmm_service):
    """Format the output as readable text."""
    output = []
    output.append("=" * 80)
    output.append("MMM MODEL INSPECTION REPORT")
    output.append("=" * 80)
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Model Structure
    output.append("MODEL STRUCTURE")
    output.append("-" * 40)
    output.append(f"Model Type: {model_info['model_type']}")
    
    if 'posterior' in model_info['structure']:
        posterior_info = model_info['structure']['posterior']
        output.append(f"Posterior Type: {posterior_info['type']}")
        output.append(f"Dimensions: {posterior_info['dims']}")
        output.append(f"Coordinates: {', '.join(posterior_info['coords']) if isinstance(posterior_info['coords'], list) else posterior_info['coords']}")
        output.append(f"Data Variables: {', '.join(posterior_info['data_vars']) if isinstance(posterior_info['data_vars'], list) else posterior_info['data_vars']}")
    
    output.append("")
    
    # Model Info
    try:
        model_status = mmm_service.get_model_info()
        output.append("MODEL INFORMATION")
        output.append("-" * 40)
        if hasattr(model_status, '__dict__'):
            # Handle dataclass or object with attributes
            for attr in ['status', 'channels', 'time_periods', 'geos']:
                if hasattr(model_status, attr):
                    value = getattr(model_status, attr)
                    output.append(f"{attr.replace('_', ' ').title()}: {value}")
        else:
            # Handle dictionary
            output.append(f"Status: {model_status.get('status', 'Unknown')}")
            output.append(f"Channels: {model_status.get('channels', 'Unknown')}")
            output.append(f"Time Periods: {model_status.get('time_periods', 'Unknown')}")
            output.append(f"Geos: {model_status.get('geos', 'Unknown')}")
        output.append("")
    except Exception as e:
        output.append(f"Model Info Error: {e}")
        output.append("")
    
    # Channel Insights
    output.append("CHANNEL INSIGHTS")
    output.append("-" * 40)
    for channel, data in channel_insights.items():
        output.append(f"\n{channel}:")
        if 'error' in data:
            output.append(f"  [ERROR] {data['error']}")
        else:
            output.append(f"  Saturation Point: {data.get('saturation_point', 'N/A')}")
            output.append(f"  Efficiency: {data.get('efficiency', 'N/A')}")
            output.append(f"  Adstock Rate: {data.get('adstock_rate', 'N/A')}")
            output.append(f"  Max Spend: {data.get('max_spend', 'N/A')}")
            output.append(f"  Max Response: {data.get('max_response', 'N/A')}")
    
    output.append("")
    
    # Contribution Summary
    output.append("CONTRIBUTION SUMMARY")
    output.append("-" * 40)
    if 'error' in contribution_summary:
        output.append(f"[ERROR] {contribution_summary['error']}")
    else:
        output.append(f"Total Time Periods: {contribution_summary.get('total_periods', 'N/A')}")
        if contribution_summary.get('date_range'):
            output.append(f"Date Range: {contribution_summary['date_range']}")
        
        if contribution_summary.get('note'):
            output.append(f"\nNote: {contribution_summary['note']}")
        elif contribution_summary.get('channels'):
            output.append("\nChannel Contributions:")
            for channel, data in contribution_summary.get('channels', {}).items():
                output.append(f"\n{channel}:")
                output.append(f"  Total: {data.get('total_contribution', 'N/A')}")
                output.append(f"  Average: {data.get('avg_contribution', 'N/A')}")
                output.append(f"  Maximum: {data.get('max_contribution', 'N/A')}")
                output.append(f"  Minimum: {data.get('min_contribution', 'N/A')}")
                output.append(f"  Data Points: {data.get('data_points', 'N/A')}")
    
    # Raw Model Structure Details
    output.append("")
    output.append("DETAILED MODEL STRUCTURE")
    output.append("-" * 40)
    for key, value in model_info['structure'].items():
        if key != 'posterior':  # Already covered above
            output.append(f"\n{key}:")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    output.append(f"  {subkey}: {subvalue}")
            else:
                output.append(f"  {value}")
    
    output.append("")
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)
    
    return "\n".join(output)


def format_json_output(model_info, channel_insights, contribution_summary, mmm_service):
    """Format the output as JSON."""
    try:
        model_status = mmm_service.get_model_info()
    except Exception as e:
        model_status = {"error": str(e)}
    
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "model_structure": model_info,
        "model_info": model_status,
        "channel_insights": channel_insights,
        "contribution_summary": contribution_summary
    }, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(description="Inspect MMM model data")
    parser.add_argument("--output-file", "-o", help="Output file path (optional)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--quiet", "-q", action="store_true", help="Don't print to terminal")
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ.setdefault('POSTGRES_USER', 'postgres')
    os.environ.setdefault('POSTGRES_PASSWORD', 'password')
    os.environ.setdefault('POSTGRES_HOST', 'localhost')
    os.environ.setdefault('POSTGRES_PORT', '5432')
    os.environ.setdefault('POSTGRES_DB', 'local')
    os.environ.setdefault('JWT_SECRET_KEY', 'your-super-secret-jwt-key')
    
    try:
        logger.info("Loading MMM model...")
        mmm_service = MMMService()
        
        logger.info("Analyzing model structure...")
        model_data = mmm_service._load_model()
        model_info = inspect_model_structure(model_data)
        
        logger.info("Getting channel insights...")
        channel_insights = get_channel_insights(mmm_service)
        
        logger.info("Getting contribution summary...")
        contribution_summary = get_contribution_summary(mmm_service)
        
        logger.info("Analysis complete!")
        
        # Format output
        if args.format == "json":
            output = format_json_output(model_info, channel_insights, contribution_summary, mmm_service)
        else:
            output = format_text_output(model_info, channel_insights, contribution_summary, mmm_service)
        
        # Print to terminal (unless quiet)
        if not args.quiet:
            print(output)  # Keep print for output display
        
        # Save to file if specified
        if args.output_file:
            output_path = Path(args.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            
            logger.info(f"Output saved to: {output_path.absolute()}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
