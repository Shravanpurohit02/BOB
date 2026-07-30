from .engine import logger

def configure_logging():
    """
    Backward-compatible logging initialization.

    Existing code expects configure_logging().
    Logging is configured automatically when engine is imported,
    so this simply returns the shared logger.
    """
    return logger

__all__ = [
    "logger",
    "configure_logging",
]
