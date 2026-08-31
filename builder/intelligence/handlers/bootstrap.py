from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from dataclasses import dataclass, field

from .base import BaseHandler
from .registry import registry


@dataclass(slots=True)
class BootstrapReport:
    loaded: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return (
            not self.failed
            and not self.duplicates
            and not self.invalid
        )


def bootstrap_handlers() -> BootstrapReport:

    report = BootstrapReport()

    registry.clear()

    package = __package__

    seen: set[str] = set()

    package_dir = Path(__file__).resolve().parent

    for module in sorted(
        pkgutil.iter_modules([str(package_dir)]),
        key=lambda m: m.name,
    ):

        name = module.name

        if name.startswith("_"):
            continue

        if name in {
            "base",
            "models",
            "registry",
            "exceptions",
            "bootstrap",
        }:
            continue

        try:
            mod = importlib.import_module(
                f"{package}.{name}"
            )

        except Exception:
            report.failed.append(name)
            continue

        handler = getattr(mod, "handler", None)

        if handler is None:
            continue

        if not isinstance(handler, BaseHandler):
            report.invalid.append(name)
            continue

        operation = getattr(handler, "operation", "").strip()

        if not operation:
            report.invalid.append(name)
            continue

        if operation in seen:
            report.duplicates.append(operation)
            continue

        seen.add(operation)

        registry.register(handler)

        report.loaded.append(operation)

    return report


__all__ = (
    "BootstrapReport",
    "bootstrap_handlers",
)
