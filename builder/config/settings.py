from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    project_name: str = Field(default="Vidhi Builder")
    environment: str = Field(default="development")
    workspace: Path = ROOT
    state_directory: Path = ROOT / ".builder" / "state"
    cache_directory: Path = ROOT / ".builder" / "cache"
    log_directory: Path = ROOT / ".builder" / "logs"

    model_config = SettingsConfigDict(
        env_prefix="VIDHI_",
        extra="ignore",
    )

settings = Settings()
