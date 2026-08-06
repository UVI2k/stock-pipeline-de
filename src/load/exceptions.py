class DatabaseConnectionError(Exception):
    """Raised when we fail to connect to Postgres. Worth retrying —
    likely transient (Neon cold start, network blip)."""
    pass