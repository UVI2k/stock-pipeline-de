import time
import logging
import functools

logger = logging.getLogger(__name__)


def retry(exceptions: tuple, max_attempts: int = 3, base_delay: float = 1.0):
    """
    Retry decorator with exponential backoff.

    Args:
        exceptions: tuple of exception types that SHOULD trigger a retry.
                    Any other exception raised by the wrapped function
                    propagates immediately, no retry.
        max_attempts: total attempts before giving up (including the first try)
        base_delay: seconds to wait before the first retry; doubles each
                    subsequent attempt (1s, 2s, 4s, ...)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {attempt} attempts: {e}"
                        )
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed "
                        f"with {type(e).__name__}: {e}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator