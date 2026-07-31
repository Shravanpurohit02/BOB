from __future__ import annotations

from .config import GuardrailConfig
from .models import (
    GuardrailReport,
    ValidationContext,
    ValidationRequest,
)
from .registry import ValidatorRegistry


class GuardrailEngine:
    """
    Coordinates execution of all registered validators.

    The engine itself contains no validation logic.
    """

    def __init__(
        self,
        registry: ValidatorRegistry,
        config: GuardrailConfig | None = None,
    ) -> None:
        self.config = config or registry.config
        self.registry = registry

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext | None = None,
    ) -> GuardrailReport:
        context = context or ValidationContext(
            config=self.config,
        )

        report = GuardrailReport()

        for validator in self.registry.enabled():
            result = validator.validate(
                request=request,
                context=context,
            )

            report.add(result)

            if (
                self.config.stop_on_error
                and result.failed
                and not validator.report_only
            ):
                break

        return report

    def validate_or_raise(
        self,
        request: ValidationRequest,
        context: ValidationContext | None = None,
    ) -> GuardrailReport:
        from .exceptions import ValidationError

        report = self.validate(request, context)

        if report.failed:
            raise ValidationError(
                "Guardrail validation failed.",
                issues=report.errors,
            )

        return report

    def run(
        self,
        request: ValidationRequest,
        context: ValidationContext | None = None,
    ) -> GuardrailReport:
        """
        Compatibility alias.
        """
        return self.validate(
            request=request,
            context=context,
        )
