from __future__ import annotations

from abc import ABC, abstractmethod

from builder.guardrails.config import GuardrailConfig
from builder.guardrails.models import (
    ValidationContext,
    ValidationRequest,
    ValidationResult,
)


class BaseValidator(ABC):
    """
    Base class for all guardrail validators.
    """

    #: Unique validator name.
    name: str = "base"

    #: Execution priority (lower executes first).
    priority: int = 100

    def __init__(self, config: GuardrailConfig | None = None) -> None:
        self.config = config or GuardrailConfig()

    @property
    def enabled(self) -> bool:
        return self.config.is_enabled(self.name)

    @property
    def report_only(self) -> bool:
        return self.config.get(self.name).report_only

    @property
    def severity(self):
        return self.config.get(self.name).severity

    @abstractmethod
    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Perform validation.

        Must never modify the repository.
        Must never call the LLM.
        Must never raise for validation failures.
        Always return ValidationResult.
        """
        raise NotImplementedError

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BaseValidator):
            return NotImplemented
        return self.priority < other.priority

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, priority={self.priority})"
        )
