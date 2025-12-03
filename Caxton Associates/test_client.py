#!/usr/bin/env python3
"""Test script for ClientAPI methods using mocked API responses"""

import json
import pandas as pd
from unittest.mock import patch, MagicMock
from client import ClientAPI, Product


def load_sample_data(filename):
    """Load sample JSON data from file"""
    with open(filename, 'r') as f:
        return json.load(f)


def test_get_implied_gbpusd_rate():
    """Test get_implied_GBPUSD_rate method with mocked API responses"""
    
    # Load sample data
    eurusd_data = load_sample_data('sample_data_eurusd.json')
    eurgbp_data = load_sample_data('sample_data_eurgbp.json')
    
    # Create client instance
    client = ClientAPI()
    
    # Mock the get_metrics method to return sample data
    with patch.object(client, 'get_metrics') as mock_get_metrics:
        # Set up side_effect to return different data based on product
        def get_metrics_side_effect(start_date, end_date, product_name, metrics):
            if product_name == Product.EURUSD:
                df = pd.DataFrame(eurusd_data)
                df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date').reset_index(drop=True)
            elif product_name == Product.EURGBP:
                df = pd.DataFrame(eurgbp_data)
                df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date').reset_index(drop=True)
            else:
                raise ValueError(f"Unknown product: {product_name}")
        
        mock_get_metrics.side_effect = get_metrics_side_effect
        
        # Test the method
        print("=" * 80)
        print("Testing get_implied_GBPUSD_rate")
        print("=" * 80)
        
        gbp_usd_rates = client.get_implied_GBPUSD_rate('2024-01-01', '2024-01-31')
        
        print(f"\nCalculated {len(gbp_usd_rates)} implied GBPUSD rates")
        print("\nFirst 10 implied GBPUSD rates:")
        print(gbp_usd_rates.head(10))
        print("\nLast 10 implied GBPUSD rates:")
        print(gbp_usd_rates.tail(10))
        print(f"\nMean implied GBPUSD rate: {gbp_usd_rates.mean():.6f}")
        print(f"Min implied GBPUSD rate: {gbp_usd_rates.min():.6f}")
        print(f"Max implied GBPUSD rate: {gbp_usd_rates.max():.6f}")
        
        # Verify the calculation: GBPUSD = EURUSD / EURGBP
        # Actually, looking at the code: gbp_usd_rates = 1 / eur_gbp_rates / eur_usd_rates
        # This seems incorrect. It should be: GBPUSD = EURUSD / EURGBP
        # But let's test what the code actually does
        
        print("\n" + "=" * 80)
        print("Verification:")
        print("=" * 80)
        eurusd_df = pd.DataFrame(eurusd_data)
        eurgbp_df = pd.DataFrame(eurgbp_data)
        eurusd_df['date'] = pd.to_datetime(eurusd_df['date'])
        eurgbp_df['date'] = pd.to_datetime(eurgbp_df['date'])
        merged = pd.merge(eurusd_df, eurgbp_df, on='date', suffixes=('_eurusd', '_eurgbp'))
        expected_gbpusd = merged['rate_eurusd'] / merged['rate_eurgbp']
        print(f"Expected GBPUSD (EURUSD/EURGBP): mean = {expected_gbpusd.mean():.6f}")
        print(f"Actual result mean: {gbp_usd_rates.mean():.6f}")
        
        return gbp_usd_rates


def test_analyze_drawdown_and_sharpe():
    """Test analyze_drawdown_and_sharpe method with mocked data"""
    
    # Load sample price data
    price_data = load_sample_data('sample_data_price_timeseries.json')
    
    # Create DataFrame
    timeseries_df = pd.DataFrame(price_data)
    timeseries_df['date'] = pd.to_datetime(timeseries_df['date'])
    timeseries_df = timeseries_df.sort_values('date').reset_index(drop=True)
    
    # Create client instance
    client = ClientAPI()
    
    print("\n" + "=" * 80)
    print("Testing analyze_drawdown_and_sharpe")
    print("=" * 80)
    
    print("\nInput timeseries data:")
    print(timeseries_df.head(10))
    print(f"\nTotal records: {len(timeseries_df)}")
    print(f"Price range: {timeseries_df['price'].min():.2f} - {timeseries_df['price'].max():.2f}")
    
    # Test the method
    client.analyze_drawdown_and_sharpe(timeseries_df)
    
    # Also test individual methods for more details
    print("\n" + "=" * 80)
    print("Detailed Analysis:")
    print("=" * 80)
    
    # Test get_drawdown_details
    max_dd_date, drawdown_begin_date = client.get_drawdown_details(timeseries_df)
    print(f"\nMax drawdown date: {max_dd_date}")
    print(f"Drawdown begin date: {drawdown_begin_date}")
    
    # Test calculate_sharpe_ratio
    sharpe = client.calculate_sharpe_ratio(timeseries_df['price'])
    print(f"\nSharpe Ratio: {sharpe:.4f}")
    
    # Manual calculation for verification
    prices = timeseries_df['price']
    returns = prices.diff()
    prices_cummax = prices.cummax()
    drawdown = prices_cummax - prices
    max_dd_idx = drawdown.idxmax()
    max_dd_value = drawdown.iloc[max_dd_idx]
    
    print(f"\nManual verification:")
    print(f"Max drawdown value: {max_dd_value:.2f}")
    print(f"Max drawdown at index: {max_dd_idx}")
    print(f"Date at max drawdown: {timeseries_df.loc[max_dd_idx, 'date']}")
    print(f"Price at max drawdown: {prices.iloc[max_dd_idx]:.2f}")
    print(f"Running max at that point: {prices_cummax.iloc[max_dd_idx]:.2f}")


def test_get_rolling_std():
    """Test get_rolling_std method"""
    
    # Load sample price data
    price_data = load_sample_data('sample_data_price_timeseries.json')
    timeseries_df = pd.DataFrame(price_data)
    timeseries_df['date'] = pd.to_datetime(timeseries_df['date'])
    timeseries_df = timeseries_df.sort_values('date').reset_index(drop=True)
    
    # Add a 'rate' column (using price as rate for testing)
    timeseries_df['rate'] = timeseries_df['price']
    
    client = ClientAPI()
    
    print("\n" + "=" * 80)
    print("Testing get_rolling_std")
    print("=" * 80)
    
    window = 10
    rolling_std = client.get_rolling_std(timeseries_df, window)
    
    print(f"\nRolling standard deviation (window={window}):")
    print(rolling_std.head(15))
    print(f"\nMean rolling std: {rolling_std.mean():.4f}")
    print(f"Max rolling std: {rolling_std.max():.4f}")


if __name__ == '__main__':
    print("Starting ClientAPI Tests")
    print("=" * 80)
    
    try:
        # Test implied GBPUSD rate
        test_get_implied_gbpusd_rate()
        
        # Test drawdown and Sharpe analysis
        test_analyze_drawdown_and_sharpe()
        
        # Test rolling std
        test_get_rolling_std()
        
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

