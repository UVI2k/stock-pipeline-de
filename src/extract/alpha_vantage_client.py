# src/extract/alpha_vantage_client.py

import os
import requests
import logging
from src.extract.exceptions import RateLimitError, InvalidSymbolError, TransientAPIError

logger = logging.getLogger(__name__)

BASE_URL = "https://www.alphavantage.co/query"


def fetch_daily_time_series(symbol: str) -> dict:
    """
    Fetch raw daily time series data for a given stock symbol from Alpha Vantage.

    Returns the raw JSON response as a dict. Does NOT clean or transform data —
    that's the transform stage's job.

    Raises:
        RateLimitError: if Alpha Vantage reports call frequency exceeded
        InvalidSymbolError: if the symbol has no data
        TransientAPIError: for network or server-side failures
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY not set in environment")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
    }

    logger.info(f"Requesting daily time series for symbol={symbol}")

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error for symbol={symbol}: {e}")
        raise TransientAPIError(f"Network failure calling Alpha Vantage: {e}") from e
        pass

    if response.status_code != 200:
        logger.warning(f"Non-200 status for symbol={symbol}: {response.status_code}")
        raise TransientAPIError(f"Alpha Vantage returned status {response.status_code} for {symbol}")
        pass

    data = response.json()

    
    if "Note" in data or "Information" in data:
        logger.warning(f"Rate limit signal received for symbol={symbol}: {data}")
        raise RateLimitError(f"Rate limit hit for {symbol}: {data.get('Note') or data.get('Information')}")

    if "Error Message" in data:
        logger.warning(f"Invalid symbol requested: {symbol}")
        raise InvalidSymbolError(f"No data for symbol {symbol}: {data['Error Message']}")

    if "Time Series (Daily)" not in data:
        # Defensive catch-all — response was 200, no known error key, but not
        # the shape we expect either. Treat as transient rather than crash.
        raise TransientAPIError(f"Unexpected response shape for {symbol}: {data}")

    logger.info(f"Successfully fetched data for symbol={symbol}")
    return data