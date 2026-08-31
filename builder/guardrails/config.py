from __future__ import annotations

from dataclasses import dataclass, field

from .constants import (
    DEFAULT_REPORT_ONLY,
    DEFAULT_STOP_ON_ERROR,
    VALIDATOR_ORDER,
)
from .models import Severity


@dataclass(slots=True)
class ValidatorConfig:
    enabled: bool = True
    report_only: bool = DEFAULT_REPORT_ONLY
    severity: Severity = Severity.ERROR


@dataclass(slots=True)
class GuardrailConfig:
    stop_on_error: bool = DEFAULT_STOP_ON_ERROR

    validators: dict[str, ValidatorConfig] = field(
        default_factory=lambda: {name: ValidatorConfig() for name in VALIDATOR_ORDER}
    )

    def is_enabled(self, validator: str) -> bool:
        cfg = self.validators.get(validator)
        return cfg is not None and cfg.enabled

    def get(self, validator: str) -> ValidatorConfig:
        return self.validators.setdefault(
            validator,
            ValidatorConfig(),
        )

    def enable(self, validator: str) -> None:
        self.get(validator).enabled = True

    def disable(self, validator: str) -> None:
        self.get(validator).enabled = False

    def set_report_only(
        self,
        validator: str,
        value: bool = True,
    ) -> None:
        self.get(validator).report_only = value

    def set_severity(
        self,
        validator: str,
        severity: Severity,
    ) -> None:
        self.get(validator).severity = severity
