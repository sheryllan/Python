# Pricing API Client Solution

This solution provides a comprehensive REST API client for daily pricing timeseries data with error handling, performance optimizations, and all required calculations.

## Files

- `pricing_api_client.py`: Main client interface and calculation functions
- `main_pricing_analysis.py`: Example usage script
- `requirements.txt`: Python dependencies

## Part A: REST API Client Interface

The `PricingAPIClient` class provides:

### Features:
- **Error Handling**:
  - Retry logic with exponential backoff
  - Timeout handling
  - HTTP error handling (4xx, 5xx)
  - JSON parsing error handling
  - Input validation

- **Performance Optimizations**:
  - Session reuse (persistent connections)
  - Caching support (using `@lru_cache` decorator)
  - Efficient DataFrame parsing
  - Batch processing capabilities

### Usage:
```python
from pricing_api_client import PricingAPIClient

client = PricingAPIClient(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3,
    cache_enabled=True
)

# Query data
df = client.query(
    start_date='2024-01-01',
    end_date='2024-12-31',
    product_name='EURUSD',
    metrics=['price']
)
```

## Part B: Calculations

### B(i): Implied GBPUSD Rate
```python
from pricing_api_client import calculate_implied_gbpusd

gbpusd_df = calculate_implied_gbpusd(eurusd_df, eurgbp_df)
# Formula: GBPUSD = EURUSD / EURGBP
```

### B(ii): Rolling Standard Deviation
```python
from pricing_api_client import rolling_std

rolling_std_series = rolling_std(price_series, window=10)
```

## Part C: Drawdown and Sharpe Ratio Analysis

### Calculations:
- **PL(T)**: `Price(T) - Price(T-1)`
- **CumulativePL(T)**: `sum(PL(S)) for all S <= T`
- **Drawdown(T)**: `CumulativePL(T') - CumulativePL(T)` where T' maximizes CumulativePL for T' <= T
- **Annualized Sharpe Ratio**: `(mean_return / std_return) * sqrt(periods_per_year)`

### Usage:
```python
from pricing_api_client import analyze_drawdown_and_sharpe

analysis = analyze_drawdown_and_sharpe(df, price_column='price')

print(f"Date of maximum drawdown: {analysis['max_drawdown_date']}")
print(f"Date when drawdown began: {analysis['drawdown_begin_date']}")
print(f"Annualized Sharpe Ratio: {analysis['annualized_sharpe_ratio']:.4f}")
```

## Installation

```bash
pip install -r requirements.txt
```

## API Response Format

The client expects a JSON response in one of these formats:

1. **Array format**:
```json
[
  {"date": "2024-01-01", "price": 1.10},
  {"date": "2024-01-02", "price": 1.11}
]
```

2. **Nested format**:
```json
{
  "data": [
    {"date": "2024-01-01", "price": 1.10},
    {"date": "2024-01-02", "price": 1.11}
  ]
}
```

3. **Timeseries format**:
```json
{
  "timeseries": [
    {"date": "2024-01-01", "price": 1.10},
    {"date": "2024-01-02", "price": 1.11}
  ]
}
```

The client automatically detects and handles these formats.

## Notes

- Replace `BASE_URL` in the scripts with your actual API endpoint
- The client handles various date formats and automatically converts them
- Error messages are logged for debugging
- The solution includes sample data generation for testing when API is unavailable

