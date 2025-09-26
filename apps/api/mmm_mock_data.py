"""
Mock MMM data generator for development and testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

def generate_mock_mmm_data() -> Dict[str, Any]:
    """Generate realistic mock MMM data for development."""
    
    # Generate date range (2 years of weekly data)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='W')
    
    # Define media channels
    channels = [
        'Google_Search', 'Google_Display', 'Facebook', 'Instagram', 
        'YouTube', 'TV', 'Radio', 'Print', 'Email', 'Direct_Mail'
    ]
    
    # Generate spend data (realistic patterns)
    np.random.seed(42)  # For reproducible results
    spend_data = {}
    
    for channel in channels:
        # Create seasonal patterns and trends
        base_spend = np.random.uniform(5000, 50000)  # Base weekly spend
        seasonal_pattern = np.sin(np.arange(len(dates)) * 2 * np.pi / 52) * 0.3  # Yearly seasonality
        trend = np.linspace(0, 0.2, len(dates))  # Growth trend
        noise = np.random.normal(0, 0.1, len(dates))  # Random variation
        
        spend = base_spend * (1 + seasonal_pattern + trend + noise)
        spend = np.maximum(spend, 0)  # Ensure non-negative
        spend_data[channel] = spend
    
    spend_df = pd.DataFrame(spend_data, index=dates)
    
    # Generate contribution data (diminishing returns effect)
    contribution_data = {}
    
    for channel in channels:
        spend = spend_data[channel]
        # Apply diminishing returns: contribution = spend^0.7 * efficiency
        efficiency = np.random.uniform(0.5, 2.0)  # Channel efficiency
        contribution = (spend ** 0.7) * efficiency
        
        # Add some noise
        contribution += np.random.normal(0, contribution * 0.05)
        contribution_data[channel] = contribution
    
    contribution_df = pd.DataFrame(contribution_data, index=dates)
    
    # Generate response curves for each channel
    response_curves = {}
    spend_ranges = np.linspace(0, 100000, 100)  # Spend range for curves
    
    for channel in channels:
        # Different saturation curves for different channels
        saturation_point = np.random.uniform(30000, 80000)
        efficiency = np.random.uniform(0.5, 2.0)
        
        # Adstock effect (carryover)
        adstock_rate = np.random.uniform(0.1, 0.5)
        
        # Generate response curve with diminishing returns
        responses = []
        for spend in spend_ranges:
            # Saturation curve: response = efficiency * spend^0.7 / (1 + spend/saturation_point)
            response = efficiency * (spend ** 0.7) / (1 + spend / saturation_point)
            responses.append(response)
        
        response_curves[channel] = {
            'spend': spend_ranges.tolist(),
            'response': responses,
            'saturation_point': saturation_point,
            'efficiency': efficiency,
            'adstock_rate': adstock_rate
        }
    
    # Generate model summary statistics
    total_contribution = contribution_df.sum().sum()
    channel_summary = {}
    
    for channel in channels:
        channel_contrib = contribution_df[channel].sum()
        channel_spend = spend_df[channel].sum()
        
        channel_summary[channel] = {
            'total_spend': float(channel_spend),
            'total_contribution': float(channel_contrib),
            'contribution_share': float(channel_contrib / total_contribution),
            'efficiency': float(channel_contrib / channel_spend) if channel_spend > 0 else 0,
            'avg_weekly_spend': float(spend_df[channel].mean()),
            'avg_weekly_contribution': float(contribution_df[channel].mean())
        }
    
    # Create mock model data structure
    mock_data = {
        'model_info': {
            'model_type': 'Google Meridian MMM',
            'version': 'mock_v1.0',
            'training_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'channels': channels,
            'data_frequency': 'weekly',
            'total_weeks': len(dates)
        },
        'spend_data': spend_df,
        'contribution_data': contribution_df,
        'response_curves': response_curves,
        'channel_summary': channel_summary,
        'model_fit': {
            'r_squared': 0.85,
            'mape': 12.3,
            'total_contribution': float(total_contribution),
            'baseline_contribution': float(total_contribution * 0.3),  # 30% baseline
            'media_contribution': float(total_contribution * 0.7)  # 70% media
        }
    }
    
    return mock_data

def get_mock_channels() -> List[str]:
    """Get list of mock media channels."""
    return [
        'Google_Search', 'Google_Display', 'Facebook', 'Instagram', 
        'YouTube', 'TV', 'Radio', 'Print', 'Email', 'Direct_Mail'
    ]

def get_mock_contribution_summary() -> Dict[str, float]:
    """Get mock contribution summary by channel."""
    mock_data = generate_mock_mmm_data()
    return {
        channel: summary['contribution_share'] 
        for channel, summary in mock_data['channel_summary'].items()
    }

def get_mock_response_curve(channel: str) -> Dict[str, List[float]]:
    """Get mock response curve for a specific channel."""
    mock_data = generate_mock_mmm_data()
    if channel in mock_data['response_curves']:
        return mock_data['response_curves'][channel]
    else:
        raise ValueError(f"Channel '{channel}' not found in mock data")

if __name__ == "__main__":
    # Test the mock data generation
    print("Generating mock MMM data...")
    data = generate_mock_mmm_data()
    
    print(f"\nModel Info: {data['model_info']}")
    print(f"\nChannels: {data['model_info']['channels']}")
    print(f"\nSpend Data Shape: {data['spend_data'].shape}")
    print(f"Contribution Data Shape: {data['contribution_data'].shape}")
    print(f"\nSample Channel Summary:")
    for channel, summary in list(data['channel_summary'].items())[:3]:
        print(f"  {channel}: {summary}")
    
    print(f"\nModel Fit: {data['model_fit']}")
    print("\n✅ Mock data generation successful!")
