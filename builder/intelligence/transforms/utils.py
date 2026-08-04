"""
Production-ready utility helpers for the BOB transformation framework.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def read_source(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def write_source(path: str, source: str) -> None:
    Path(path).write_text(source, encoding="utf-8")


def file_exists(path: str) -> bool:
    return Path(path).exists()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    return sha256_text(read_source(path))


def ensure_directory(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def normalize_path(path: str) -> str:
    return str(Path(path).resolve()).replace("\\", "/")


__all__ = (
    "read_source",
    "write_source",
    "file_exists",
    "sha256_text",
    "sha256_file",
    "ensure_directory",
    "normalize_path",
)
