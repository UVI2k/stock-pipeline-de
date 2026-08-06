# src/load/postgres_loader.py

import os
import logging
import psycopg2
from src.utils.retry import retry
from src.load.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

UPSERT_QUERY = """
INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (symbol, date)
DO UPDATE SET
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume;
"""


@retry(exceptions=(DatabaseConnectionError,), max_attempts=3, base_delay=1.0)
def load_rows(rows: list[dict]) -> int:
    """
    Upsert a list of clean row dicts into the stock_prices table.
    Returns the number of rows written.
    """
    if not rows:
        logger.info("No rows to load, skipping database write")
        return 0

    db_url = os.getenv("NEON_DATABASE_URL")

    try:
        conn = psycopg2.connect(db_url)
    except psycopg2.OperationalError as e:
        logger.warning(f"Database connection failed: {type(e).__name__}")
        raise DatabaseConnectionError("Could not connect to database")

    try:
        with conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(UPSERT_QUERY, (
                        row["symbol"], row["date"], row["open"],
                        row["high"], row["low"], row["close"], row["volume"],
                    ))
        logger.info(f"Loaded {len(rows)} rows into stock_prices")
        return len(rows)
    finally:
        conn.close()