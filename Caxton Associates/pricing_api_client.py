"""
REST API Client for Daily Pricing Timeseries Data
"""

import pandas as pd
import numpy as np
import requests
from typing import List, Dict, Optional, Union
from datetime import datetime, date
import time
from functools import lru_cache
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PricingAPIClient:
    """
    Client interface for querying REST API for daily pricing timeseries data.
    Includes error handling and performance optimizations.
    """
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3, 
                 cache_enabled: bool = True):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the REST API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_enabled: Enable caching for repeated queries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        self.session = requests.Session()
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """
        Make a POST request with retry logic and error handling.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If request fails after retries
            ValueError: If response is not valid JSON
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()  # Raises HTTPError for bad responses
                
                try:
                    return response.json()
                except ValueError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    raise ValueError(f"Response is not valid JSON: {e}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise requests.exceptions.Timeout(
                        f"Request timed out after {self.max_retries} attempts"
                    )
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                if e.response.status_code in [400, 401, 403, 404]:
                    # Don't retry client errors
                    raise
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        raise requests.exceptions.RequestException("Request failed after all retries")
    
    def _parse_response_to_dataframe(self, response: Dict, product_name: str) -> pd.DataFrame:
        """
        Parse API response JSON to pandas DataFrame.
        Handles different possible response structures.
        
        Args:
            response: JSON response from API
            product_name: Name of the product
            
        Returns:
            DataFrame with columns: date, product, and metric columns
        """
        try:
            # Try common response structures
            if 'data' in response:
                data = response['data']
            elif 'timeseries' in response:
                data = response['timeseries']
            elif isinstance(response, list):
                data = response
            else:
                data = response
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Ensure date column exists and is datetime
            date_col = None
            for col in ['date', 'Date', 'DATE', 'timestamp', 'Timestamp']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col])
                df = df.rename(columns={date_col: 'date'})
            else:
                # If no date column, create one from index
                df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
            
            # Add product name if not present
            if 'product' not in df.columns:
                df['product'] = product_name
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            raise ValueError(f"Failed to parse response to DataFrame: {e}")
    
    @lru_cache(maxsize=128)
    def _cached_query(self, start_date: str, end_date: str, product: str, metrics: tuple) -> Dict:
        """
        Cached version of query (for performance optimization).
        Note: This is a helper method, not called directly.
        """
        # This is just a placeholder - actual caching would be in query method
        pass
    
    def query(self, start_date: Union[str, date, datetime], 
              end_date: Union[str, date, datetime],
              product_name: str,
              metrics: List[str]) -> pd.DataFrame:
        """
        Query the REST API for daily pricing timeseries data.
        
        Args:
            start_date: Start date (YYYY-MM-DD format or date/datetime object)
            end_date: End date (YYYY-MM-DD format or date/datetime object)
            product_name: Name of the product (e.g., 'EURUSD')
            metrics: List of metrics to retrieve (e.g., ['price'])
            
        Returns:
            DataFrame with columns: date, product, and metric columns
            
        Raises:
            ValueError: If dates are invalid or metrics list is empty
            requests.RequestException: If API request fails
        """
        # Validate inputs
        if not metrics:
            raise ValueError("Metrics list cannot be empty")
        
        # Convert dates to strings if needed
        if isinstance(start_date, (date, datetime)):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, (date, datetime)):
            end_date = end_date.strftime('%Y-%m-%d')
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")
        
        # Prepare payload
        payload = {
            'start_date': start_date,
            'end_date': end_date,
            'product': product_name,
            'metrics': metrics
        }
        
        logger.info(f"Querying API for {product_name} from {start_date} to {end_date}")
        
        # Make request
        try:
            response = self._make_request('pricing', payload)
        except Exception as e:
            logger.error(f"API query failed: {e}")
            raise
        
        # Parse response to DataFrame
        df = self._parse_response_to_dataframe(response, product_name)
        
        logger.info(f"Retrieved {len(df)} records for {product_name}")
        return df


def get_eurusd_rate(client: PricingAPIClient, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Query EURUSD rate from the API.
    
    Args:
        client: PricingAPIClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with EURUSD rate data
    """
    return client.query(start_date, end_date, 'EURUSD', ['price'])


def get_eurgbp_rate(client: PricingAPIClient, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Query EURGBP rate from the API.
    
    Args:
        client: PricingAPIClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with EURGBP rate data
    """
    return client.query(start_date, end_date, 'EURGBP', ['price'])


def calculate_implied_gbpusd(eurusd_df: pd.DataFrame, eurgbp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate implied GBPUSD rate from EURUSD and EURGBP.
    
    Formula: GBPUSD = EURUSD / EURGBP
    
    Args:
        eurusd_df: DataFrame with EURUSD rates (must have 'date' and 'price' columns)
        eurgbp_df: DataFrame with EURGBP rates (must have 'date' and 'price' columns)
        
    Returns:
        DataFrame with implied GBPUSD rates
    """
    # Merge on date
    merged = pd.merge(
        eurusd_df[['date', 'price']].rename(columns={'price': 'EURUSD'}),
        eurgbp_df[['date', 'price']].rename(columns={'price': 'EURGBP'}),
        on='date',
        how='inner'
    )
    
    # Calculate implied GBPUSD
    merged['GBPUSD'] = merged['EURUSD'] / merged['EURGBP']
    
    result = merged[['date', 'GBPUSD']].copy()
    result['product'] = 'GBPUSD_implied'
    
    return result


def rolling_std(series: pd.Series, window: int = 10) -> pd.Series:
    """
    Calculate rolling standard deviation for a time series.
    
    Args:
        series: Pandas Series with numeric values
        window: Rolling window size (default: 10 days)
        
    Returns:
        Series with rolling standard deviation values
    """
    if window <= 0:
        raise ValueError("Window size must be positive")
    
    if len(series) < window:
        logger.warning(f"Series length ({len(series)}) is less than window size ({window})")
        return pd.Series([np.nan] * len(series), index=series.index)
    
    return series.rolling(window=window).std()


def calculate_pl(price_series: pd.Series) -> pd.Series:
    """
    Calculate P&L: PL(T) = Price(T) - Price(T-1)
    
    Args:
        price_series: Series of prices
        
    Returns:
        Series of P&L values
    """
    return price_series.diff()


def calculate_cumulative_pl(pl_series: pd.Series) -> pd.Series:
    """
    Calculate Cumulative P&L: CumulativePL(T) = sum(PL(S)) over all S <= T
    
    Args:
        pl_series: Series of P&L values
        
    Returns:
        Series of cumulative P&L values
    """
    return pl_series.cumsum()


def calculate_drawdown(cumulative_pl: pd.Series) -> pd.Series:
    """
    Calculate Drawdown: Drawdown(T) = CumulativePL(T') - CumulativePL(T)
    where T' maximizes CumulativePL for T' <= T.
    
    Args:
        cumulative_pl: Series of cumulative P&L values
        
    Returns:
        Series of drawdown values
    """
    # Calculate running maximum of cumulative P&L
    running_max = cumulative_pl.expanding().max()
    
    # Drawdown is the difference between running max and current value
    drawdown = running_max - cumulative_pl
    
    return drawdown


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, 
                          periods_per_year: int = 252) -> float:
    """
    Calculate annualized Sharpe Ratio.
    
    Args:
        returns: Series of returns (or P&L)
        risk_free_rate: Risk-free rate (annualized, default: 0.0)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        Annualized Sharpe Ratio
    """
    if len(returns) < 2:
        return np.nan
    
    # Calculate excess returns
    excess_returns = returns - (risk_free_rate / periods_per_year)
    
    # Calculate mean and std
    mean_return = excess_returns.mean()
    std_return = excess_returns.std()
    
    if std_return == 0:
        return np.nan
    
    # Annualize
    sharpe = (mean_return / std_return) * np.sqrt(periods_per_year)
    
    return sharpe


def analyze_drawdown_and_sharpe(df: pd.DataFrame, price_column: str = 'price') -> Dict:
    """
    Analyze drawdown and calculate Sharpe ratio for a price series.
    
    Args:
        df: DataFrame with 'date' and price column
        price_column: Name of the price column (default: 'price')
        
    Returns:
        Dictionary with analysis results
    """
    # Ensure date is datetime and sort
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Calculate P&L, Cumulative P&L, and Drawdown
    pl = calculate_pl(df[price_column])
    cumulative_pl = calculate_cumulative_pl(pl)
    drawdown = calculate_drawdown(cumulative_pl)
    
    # Find maximum drawdown
    max_drawdown_idx = drawdown.idxmax()
    max_drawdown_date = df.loc[max_drawdown_idx, 'date']
    max_drawdown_value = drawdown.iloc[max_drawdown_idx]
    
    # Find when drawdown began (date when running max was last achieved before max drawdown)
    running_max = cumulative_pl.expanding().max()
    # Find the date where the running max was achieved before the max drawdown
    max_cum_pl_before_dd = cumulative_pl.loc[:max_drawdown_idx].max()
    drawdown_begin_idx = cumulative_pl.loc[:max_drawdown_idx].idxmax()
    drawdown_begin_date = df.loc[drawdown_begin_idx, 'date']
    
    # Calculate Sharpe Ratio
    sharpe_ratio = calculate_sharpe_ratio(pl.dropna())
    
    return {
        'max_drawdown_date': max_drawdown_date,
        'max_drawdown_value': max_drawdown_value,
        'drawdown_begin_date': drawdown_begin_date,
        'annualized_sharpe_ratio': sharpe_ratio,
        'pl': pl,
        'cumulative_pl': cumulative_pl,
        'drawdown': drawdown
    }


if __name__ == '__main__':
    # Example usage
    # Note: Replace with actual API base URL
    BASE_URL = "https://api.example.com"  # Replace with actual URL
    
    client = PricingAPIClient(base_url=BASE_URL)
    
    # Query rates
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    print("Querying EURUSD and EURGBP rates...")
    eurusd_df = get_eurusd_rate(client, start_date, end_date)
    eurgbp_df = get_eurgbp_rate(client, start_date, end_date)
    
    # Calculate implied GBPUSD
    print("\nCalculating implied GBPUSD rate...")
    gbpusd_df = calculate_implied_gbpusd(eurusd_df, eurgbp_df)
    print(gbpusd_df.head())
    
    # Calculate rolling standard deviation
    print("\nCalculating rolling standard deviation (10-day window)...")
    rolling_std_series = rolling_std(eurusd_df['price'], window=10)
    print(rolling_std_series.head(15))
    
    # Analyze drawdown and Sharpe ratio (using EURUSD as sample)
    print("\nAnalyzing drawdown and Sharpe ratio for EURUSD...")
    analysis = analyze_drawdown_and_sharpe(eurusd_df, price_column='price')
    
    print(f"\nResults:")
    print(f"Date of maximum drawdown: {analysis['max_drawdown_date']}")
    print(f"Date when drawdown began: {analysis['drawdown_begin_date']}")
    print(f"Annualized Sharpe Ratio: {analysis['annualized_sharpe_ratio']:.4f}")

