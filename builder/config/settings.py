from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[2]


def _path_from_environment(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser().resolve()
    return default.resolve()


@dataclass(slots=True)
class Settings:
    """
    Central runtime configuration authority.

    Workspace-owned artifacts remain attached to the selected workspace.
    Runtime-owned data is resolved independently so BOB can be embedded
    inside Android or another host without relying on process CWD.
    """

    workspace: Path = ROOT

    state_directory: Path = ROOT / ".builder" / "state"
    cache_directory: Path = ROOT / ".builder" / "cache"
    log_directory: Path = ROOT / ".builder" / "logs"

    runtime_directory: Path = ROOT / ".builder"

    def resolve_runtime_directory(self) -> Path:
        return _path_from_environment(
            "BOB_RUNTIME_DIRECTORY",
            self.runtime_directory,
        )

    def resolve_state_directory(self) -> Path:
        return _path_from_environment(
            "BOB_STATE_DIRECTORY",
            self.resolve_runtime_directory() / "state",
        )

    def resolve_cache_directory(self) -> Path:
        return _path_from_environment(
            "BOB_CACHE_DIRECTORY",
            self.resolve_runtime_directory() / "cache",
        )

    def resolve_log_directory(self) -> Path:
        return _path_from_environment(
            "BOB_LOG_DIRECTORY",
            self.resolve_runtime_directory() / "logs",
        )

    def resolve_output_directory(self) -> Path:
        return _path_from_environment(
            "BOB_OUTPUT_DIRECTORY",
            self.resolve_runtime_directory() / "output",
        )

    def resolve_memory_directory(self) -> Path:
        return _path_from_environment(
            "BOB_MEMORY_DIRECTORY",
            self.resolve_runtime_directory() / "memory",
        )

    def resolve_transaction_directory(self) -> Path:
        return _path_from_environment(
            "BOB_TRANSACTION_DIRECTORY",
            self.resolve_runtime_directory() / "transactions",
        )

    def resolve_snapshot_directory(self) -> Path:
        return _path_from_environment(
            "BOB_SNAPSHOT_DIRECTORY",
            self.resolve_runtime_directory() / "snapshots",
        )

    def ensure_runtime_directories(self) -> None:
        directories = (
            self.resolve_runtime_directory(),
            self.resolve_state_directory(),
            self.resolve_cache_directory(),
            self.resolve_log_directory(),
            self.resolve_output_directory(),
            self.resolve_memory_directory(),
            self.resolve_transaction_directory(),
            self.resolve_snapshot_directory(),
        )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()


__all__ = (
    "ROOT",
    "Settings",
    "settings",
)
