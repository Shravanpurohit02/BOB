from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Environment:
    os_name: str
    platform_name: str
    python_version: str
    cwd: Path
    home: Path
    termux: bool

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def cwd_exists(self) -> bool:
        return self.cwd.exists()

    @property
    def home_exists(self) -> bool:
        return self.home.exists()

    @property
    def python_major(self) -> int:
        return sys.version_info.major

    @property
    def python_minor(self) -> int:
        return sys.version_info.minor

    def to_dict(self) -> dict[str, Any]:
        return {
            "os_name": self.os_name,
            "platform_name": self.platform_name,
            "python_version": self.python_version,
            "cwd": str(self.cwd),
            "home": str(self.home),
            "termux": self.termux,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Environment":
        return cls(
            os_name=data["os_name"],
            platform_name=data["platform_name"],
            python_version=data["python_version"],
            cwd=Path(data["cwd"]),
            home=Path(data["home"]),
            termux=data["termux"],
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def detect(cls) -> "Environment":
        prefix = os.environ.get("PREFIX", "")
        return cls(
            os_name=os.name,
            platform_name=platform.platform(),
            python_version=sys.version.split()[0],
            cwd=Path.cwd(),
            home=Path.home(),
            termux="com.termux" in prefix,
        )
