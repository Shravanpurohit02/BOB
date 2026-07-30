import logging
from logging.handlers import RotatingFileHandler

from builder.config import settings

LOGGER_NAME = "vidhi_builder"

logger = logging.getLogger(LOGGER_NAME)

def configure_logging() -> logging.Logger:
    if logger.handlers:
        return logger

    settings.log_directory.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler = RotatingFileHandler(
        settings.log_directory / "builder.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
