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
        contribution = np.maximum(contribution, 0)
        contribution_data[channel] = contribution
    
    contribution_df = pd.DataFrame(contribution_data, index=dates)
    
    # Generate response curves for each channel
    response_curves = {}
    for channel in channels:
        max_spend = spend_data[channel].max() * 2
        spend_points = np.linspace(0, max_spend, 50)
        
        # Hill saturation parameters
        alpha = np.random.uniform(0.5, 2.0)  # Shape parameter
        ec = np.random.uniform(max_spend * 0.3, max_spend * 0.7)  # Half-saturation point
        
        # Calculate response using Hill saturation
        response = (spend_points ** alpha) / (ec ** alpha + spend_points ** alpha)
        response *= max_spend * np.random.uniform(0.5, 1.5)  # Scale response
        
        response_curves[channel] = {
            'spend': spend_points.tolist(),
            'response': response.tolist(),
            'alpha': alpha,
            'ec': ec,
            'saturation_point': ec,
            'efficiency': alpha
        }
    
    # Create mock model structure
    mock_model = {
        'type': 'mock_meridian_model',
        'version': '1.0.0-mock',
        'channels': channels,
        'dates': dates,
        'spend_data': spend_df,
        'contribution_data': contribution_df,
        'response_curves': response_curves,
        'metadata': {
            'training_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'data_frequency': 'weekly',
            'total_weeks': len(dates),
            'total_channels': len(channels),
            'data_source': 'mock_generator'
        }
    }
    
    return mock_model


def get_mock_channels() -> List[str]:
    """Get list of mock channel names."""
    return [
        'Google_Search', 'Google_Display', 'Facebook', 'Instagram', 
        'YouTube', 'TV', 'Radio', 'Print', 'Email', 'Direct_Mail'
    ]


def generate_mock_contribution_summary(channels: List[str]) -> Dict[str, Dict[str, float]]:
    """Generate mock contribution summary statistics."""
    summary = {}
    
    np.random.seed(42)
    for channel in channels:
        # Generate realistic summary stats
        total = np.random.uniform(50000, 500000)
        mean = total / 104  # Assuming 2 years of weekly data
        
        summary[channel] = {
            'total_contribution': total,
            'mean_contribution': mean,
            'max_contribution': mean * np.random.uniform(1.5, 3.0),
            'min_contribution': mean * np.random.uniform(0.1, 0.5),
            'std_contribution': mean * np.random.uniform(0.2, 0.8),
            'efficiency_score': np.random.uniform(0.3, 2.5)
        }
    
    return summary


def generate_mock_response_curve(channel: str, max_spend: float = 100000) -> Dict[str, Any]:
    """Generate a mock response curve for a specific channel."""
    np.random.seed(hash(channel) % 2**32)  # Deterministic but channel-specific
    
    spend_points = np.linspace(0, max_spend, 50)
    
    # Hill saturation parameters
    alpha = np.random.uniform(0.5, 2.0)
    ec = np.random.uniform(max_spend * 0.2, max_spend * 0.8)
    
    # Calculate response
    response = (spend_points ** alpha) / (ec ** alpha + spend_points ** alpha)
    response *= max_spend * np.random.uniform(0.3, 1.2)
    
    return {
        'channel': channel,
        'spend': spend_points.tolist(),
        'response': response.tolist(),
        'saturation_point': ec,
        'efficiency': alpha,
        'adstock_rate': np.random.uniform(0.1, 0.9),
        'max_response': float(response.max()),
        'marginal_roi': float(np.gradient(response, spend_points).mean())
    }
