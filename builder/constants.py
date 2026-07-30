from pathlib import Path

PROJECT_NAME = "Vidhi Builder"

ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / ".builder"
STATE_DIR = DATA_DIR / "state"
CACHE_DIR = DATA_DIR / "cache"
LOG_DIR = DATA_DIR / "logs"
TEMP_DIR = DATA_DIR / "temp"

DIRECTORIES = (
    DATA_DIR,
    STATE_DIR,
    CACHE_DIR,
    LOG_DIR,
    TEMP_DIR,
)
