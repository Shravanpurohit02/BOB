from pathlib import Path

from builder.config import settings


PROJECT_NAME = "BOB"

ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT / "config"

# Runtime-owned storage is exposed through the compatibility constants below.
# The actual locations are resolved by builder.config.settings.
DATA_DIR = settings.resolve_runtime_directory()
STATE_DIR = settings.resolve_state_directory()
CACHE_DIR = settings.resolve_cache_directory()
LOG_DIR = settings.resolve_log_directory()
TEMP_DIR = DATA_DIR / "temp"

DIRECTORIES = (
    DATA_DIR,
    STATE_DIR,
    CACHE_DIR,
    LOG_DIR,
    TEMP_DIR,
)

__all__ = (
    "PROJECT_NAME",
    "ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "STATE_DIR",
    "CACHE_DIR",
    "LOG_DIR",
    "TEMP_DIR",
    "DIRECTORIES",
)
