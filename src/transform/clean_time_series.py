import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def clean_time_series(raw_data: dict, symbol: str) -> list[dict]:
    """
    Convert raw Alpha Vantage TIME_SERIES_DAILY JSON into a list of clean,
    typed row dicts ready for database insertion.

    Args:
        raw_data: the raw dict returned by fetch_daily_time_series()
        symbol: the stock ticker this data belongs to (not reliably present
                in raw_data itself — passed explicitly, see design note above)

    Returns:
        List of dicts, one per trading day:
        [{"symbol": "AAPL", "date": date(2026,7,24), "open": 191.50, ...}, ...]
    """
    time_series = raw_data.get("Time Series (Daily)")
    if not time_series:
        
        logger.warning(f"No time series data found for symbol={symbol}")
        return []

    rows = []
    for date_str, values in time_series.items():
        try:
            row = {
                "symbol": symbol,
                "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            }
            rows.append(row)
        except (KeyError, ValueError) as e:
            logger.warning(
                f"Skipping malformed row for symbol={symbol}, date={date_str}: {e}"
            )
            continue

    logger.info(f"Transformed {len(rows)} rows for symbol={symbol}")
    return rows