"""Conversion of BOB domain results into JSON-safe application data."""

from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class SerializationError(TypeError):
    """Raised when a value cannot be represented by the bridge serializer."""


def to_json_safe(value: Any) -> Any:
    """Recursively convert supported BOB values into JSON-safe primitives."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Enum):
        return to_json_safe(value.value)

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value):
        return {
            field.name: to_json_safe(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, (str, int, float, bool)):
                key = str(key)
            result[str(key)] = to_json_safe(item)
        return result

    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_json_safe(item) for item in value]

    if hasattr(value, "to_dict") and callable(value.to_dict):
        return to_json_safe(value.to_dict())

    if hasattr(value, "__dict__"):
        return {
            str(key): to_json_safe(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }

    raise SerializationError(
        f"Unsupported bridge response value: {type(value).__name__}"
    )
