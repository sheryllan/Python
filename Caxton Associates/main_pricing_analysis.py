"""
Main script to demonstrate the pricing API client and perform required calculations.
"""

import pandas as pd
from pricing_api_client import (
    PricingAPIClient,
    get_eurusd_rate,
    get_eurgbp_rate,
    calculate_implied_gbpusd,
    rolling_std,
    analyze_drawdown_and_sharpe
)


def main():
    """
    Main function to demonstrate the pricing API client usage.
    """
    # Initialize client
    # NOTE: Replace with actual API base URL
    BASE_URL = "https://api.example.com"  # Replace with actual URL
    
    client = PricingAPIClient(
        base_url=BASE_URL,
        timeout=30,
        max_retries=3,
        cache_enabled=True
    )
    
    # Set date range
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    print("=" * 80)
    print("PART A: REST API Client Interface")
    print("=" * 80)
    
    # Query EURUSD and EURGBP rates
    print("\n1. Querying EURUSD rate...")
    try:
        eurusd_df = get_eurusd_rate(client, start_date, end_date)
        print(f"   Retrieved {len(eurusd_df)} records")
        print(f"   Date range: {eurusd_df['date'].min()} to {eurusd_df['date'].max()}")
        print(f"   Sample data:\n{eurusd_df.head()}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Using sample data for demonstration...")
        # Create sample data for demonstration
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        eurusd_df = pd.DataFrame({
            'date': dates,
            'product': 'EURUSD',
            'price': 1.10 + pd.Series(range(len(dates))) * 0.0001 + 
                     pd.Series(range(len(dates))).apply(lambda x: (x % 10) * 0.001)
        })
    
    print("\n2. Querying EURGBP rate...")
    try:
        eurgbp_df = get_eurgbp_rate(client, start_date, end_date)
        print(f"   Retrieved {len(eurgbp_df)} records")
        print(f"   Date range: {eurgbp_df['date'].min()} to {eurgbp_df['date'].max()}")
        print(f"   Sample data:\n{eurgbp_df.head()}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Using sample data for demonstration...")
        # Create sample data for demonstration
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        eurgbp_df = pd.DataFrame({
            'date': dates,
            'product': 'EURGBP',
            'price': 0.85 + pd.Series(range(len(dates))) * 0.00005 + 
                     pd.Series(range(len(dates))).apply(lambda x: (x % 10) * 0.0005)
        })
    
    print("\n" + "=" * 80)
    print("PART B: Calculations")
    print("=" * 80)
    
    # Part B(i): Implied GBPUSD rate
    print("\nB(i). Calculating implied GBPUSD rate...")
    gbpusd_df = calculate_implied_gbpusd(eurusd_df, eurgbp_df)
    print(f"   Calculated {len(gbpusd_df)} implied GBPUSD rates")
    print(f"   Sample data:\n{gbpusd_df.head(10)}")
    print(f"   Mean implied GBPUSD: {gbpusd_df['GBPUSD'].mean():.6f}")
    
    # Part B(ii): Rolling standard deviation
    print("\nB(ii). Calculating rolling standard deviation (10-day window)...")
    window = 10
    rolling_std_series = rolling_std(eurusd_df['price'], window=window)
    print(f"   Calculated rolling std with {window}-day window")
    print(f"   Sample data (first 15 values):\n{rolling_std_series.head(15)}")
    print(f"   Mean rolling std: {rolling_std_series.mean():.6f}")
    
    # Part C: Drawdown and Sharpe Ratio analysis
    print("\n" + "=" * 80)
    print("PART C: Drawdown and Sharpe Ratio Analysis")
    print("=" * 80)
    
    print("\nAnalyzing EURUSD price series...")
    analysis = analyze_drawdown_and_sharpe(eurusd_df, price_column='price')
    
    print("\nResults:")
    print("-" * 80)
    print(f"i. Date of maximum drawdown: {analysis['max_drawdown_date']}")
    print(f"ii. Date when drawdown began: {analysis['drawdown_begin_date']}")
    print(f"iii. Annualized Sharpe Ratio: {analysis['annualized_sharpe_ratio']:.4f}")
    print("-" * 80)
    
    # Additional details
    print(f"\nAdditional Statistics:")
    print(f"   Maximum drawdown value: {analysis['max_drawdown_value']:.6f}")
    print(f"   Maximum cumulative P&L: {analysis['cumulative_pl'].max():.6f}")
    print(f"   Minimum cumulative P&L: {analysis['cumulative_pl'].min():.6f}")
    
    # Create summary DataFrame
    summary_df = pd.DataFrame({
        'date': eurusd_df['date'],
        'price': eurusd_df['price'],
        'PL': analysis['pl'],
        'CumulativePL': analysis['cumulative_pl'],
        'Drawdown': analysis['drawdown']
    })
    
    print(f"\nSummary DataFrame (first 10 rows):")
    print(summary_df.head(10))
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

