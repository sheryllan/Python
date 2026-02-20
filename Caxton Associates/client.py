from numpy import str_
import pandas as pd
import requests
import logging
from datetime import datetime
from enum import Enum
import numpy as np
import asyncio
import aiohttp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Product(str, Enum):
    EURUSD = 'EURUSD'
    EURGBP = 'EURGBP'


class ClientAPI:

    BASE_URL = 'https://api.example.com'
    TIMEOUT_SECONDS = 10

    def _normalize_dates(self, start_date: str, end_date: str) -> tuple[str, str]:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            logger.error('Invalid date format')
            raise ValueError('Invalid date format')
        if start_dt > end_dt:
            raise ValueError('start_date must be <= end_date')
        return start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d')

    def _build_dataframe(self, data: dict | list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(data)
        date_col = 'date'
        if date_col not in df.columns:
            raise ValueError(f'Date column {date_col} not found in response')

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if df[date_col].isna().sum() > 0:
            raise ValueError(f'Date column {date_col} has NaN values')

        return df.sort_values(date_col).reset_index(drop=True)

    def get_metrics(self, start_date: str, end_date: str, product_name: str, metrics: list[str]):
        if not metrics:
            logger.error('Metrics list cannot be empty')
            raise ValueError("Metrics list cannot be empty")

        start_date, end_date = self._normalize_dates(start_date, end_date)
        
        payload = {
            'start_date': start_date,
            'end_date': end_date,
            'product_name': product_name,
            'metrics': metrics
        }

        try:
            response = requests.post(
                self.BASE_URL,
                json=payload,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
           
        except requests.exceptions.RequestException as e:
            # RequestException includes Timeout, HTTPError, and ConnectionError
            logger.error(f'Failed to get metrics: {e}')
            raise

        try:
            data = response.json()
        except ValueError as e:
            logger.error(f'Invalid JSON response: {e}')
            raise ValueError('Invalid JSON response')

        if isinstance(data, dict) and data.get('error'):
            raise ValueError(f"API error: {data.get('error')}")

        return self._build_dataframe(data)

    async def get_metrics_async(self, start_date: str, end_date: str, product_name: str, metrics: list[str]):
        if not metrics:
            logger.error('Metrics list cannot be empty')
            raise ValueError("Metrics list cannot be empty")

        start_date, end_date = self._normalize_dates(start_date, end_date)

        payload = {
            'start_date': start_date,
            'end_date': end_date,
            'product_name': product_name,
            'metrics': metrics
        }

        timeout = aiohttp.ClientTimeout(total=self.TIMEOUT_SECONDS)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.BASE_URL, json=payload) as response:
                    response.raise_for_status()
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError as e:
                        logger.error(f'Invalid JSON response: {e}')
                        raise ValueError('Invalid JSON response')
        except aiohttp.ClientError as e:
            logger.error(f'Failed to get metrics (async): {e}')
            raise

        if isinstance(data, dict) and data.get('error'):
            raise ValueError(f"API error: {data.get('error')}")

        return self._build_dataframe(data)


    def get_implied_GBPUSD_rate(self, start_date: str, end_date: str):
        eur_usd_rates = self.get_metrics(start_date, end_date, Product.EURUSD, ['rate']).set_index('date')['rate']
        eur_gbp_rates = self.get_metrics(start_date, end_date, Product.EURGBP, ['rate']).set_index('date')['rate']
        gbp_usd_rates = eur_usd_rates / eur_gbp_rates
        return gbp_usd_rates

    def get_rolling_std(self, timeseries: pd.DataFrame, window: int):
        std_df = timeseries['rate'].rolling(window=window).std()
        return std_df

    def get_drawdown_details(self, timeseries: pd.DataFrame):
        # nan prices are forward filled
        prices = timeseries['price'].fillna(method='ffill')
        prices_cummax = prices.cummax()
        drawdown = prices_cummax - prices
        max_drawdown_idx = drawdown.idxmax()
        max_drawdown_date = timeseries.loc[max_drawdown_idx, 'date']

        drawdown_begin_idx = prices_cummax.loc[:max_drawdown_idx].idxmax()
        drawdown_begin_date = timeseries.loc[drawdown_begin_idx, 'date']
        
        return max_drawdown_date, drawdown_begin_date
        

    def calculate_sharpe_ratio(self, prices: pd.Series, risk_free_rate: float = 0.0, 
                          periods_per_year: int = 252) -> float:
        returns = prices.diff()
        excess_returns = returns - risk_free_rate / periods_per_year
        mean_return = excess_returns.mean()
        std_return = excess_returns.std()
        if std_return == 0:
            return np.nan
        return mean_return / std_return * np.sqrt(periods_per_year)


    def analyze_drawdown_and_sharpe(self, timeseries: pd.DataFrame):
        max_drawdown_date, drawdown_begin_date = self.get_drawdown_details(timeseries)
        print(f"Date of maximum drawdown: {max_drawdown_date}")
        print(f"Date when drawdown began: {drawdown_begin_date}")

        sharpe_ratio = self.calculate_sharpe_ratio(timeseries['price'], 0, 252)
        print(f"Annualized Sharpe Ratio: {sharpe_ratio:.4f}")


    # def get_metrics_cached(self, start_date: str, end_date: str, product_name: str, metrics: list[str]):
    #     return self.get_metrics(start_date, end_date, product_name, metrics)


