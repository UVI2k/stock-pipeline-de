# src/extract/exceptions.py

class AlphaVantageError(Exception):
    """Base exception for all Alpha Vantage extraction failures."""
    pass


class RateLimitError(AlphaVantageError):
    """Raised when Alpha Vantage signals we've hit their call frequency limit.
    This IS worth retrying, but only after waiting.
    """
    pass


class InvalidSymbolError(AlphaVantageError):
    """Raised when the API responds but the symbol has no data.
    This is NOT worth retrying — retrying bad input wastes quota.
    """
    pass


class TransientAPIError(AlphaVantageError):
    """Raised for network-level or 5xx server errors.
    This IS worth retrying — likely temporary.
    """
    pass