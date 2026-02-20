"""Utility module for parsing contract tickers."""

from typing import Tuple
from datetime import date


MONTH_CODES = {
        'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
        'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12
    }


def get_expiration_date(year: int, month: int) -> date:
    """Get a datetime object of expiration date from year and month"""
    return date(year, month, 1)


def parse_year_code(year_code: int, reference_year: int = date.today().year) -> int:
    """Get the year from the year code, assuming the year code is a 1-digit number.

    Parameters
    ----------
    year_code: 1-digit integer, which means the code represents a specific year in a decade
    reference_year: A year the target decade is inclusive of, use current year by default
    """
    return reference_year // 10 * 10 + year_code


def parse_contract(contract_ticker: str) -> Tuple[str, date]:
    """Parse the expiration date from a futures contract ticker

    Parameters
    ----------
    contract_ticker: Contract ticker (e.g., 'GCQ4 Comdty')

    Return
    ------
    Tuple of (product_code, expiry)

    Examples
    --------
    'GCQ4 Comdty' -> (GC, 2024-08-01)
    """
    parts = contract_ticker.split()
    if len(parts) < 1:
        raise ValueError(f"Invalid contract ticker format: {contract_ticker}")

    ticker_part = parts[0]
    if len(ticker_part) < 3:
        raise ValueError(f"Contract ticker too short: {ticker_part}")

    product_code = ticker_part[:-2]
    month_code = ticker_part[-2]
    year_code = ticker_part[-1]

    try:
        year = parse_year_code(int(year_code))
    except ValueError:
        raise ValueError(f"Invalid year code: {year_code}")

    if month_code not in MONTH_CODES:
        raise ValueError(f"Invalid month code: {month_code}")
    month = MONTH_CODES[month_code]

    return product_code, get_expiration_date(year, month)
