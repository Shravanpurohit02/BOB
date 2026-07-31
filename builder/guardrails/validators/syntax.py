from __future__ import annotations

import ast

from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class SyntaxValidator(BaseValidator):
    """
    Validates Python syntax for generated source files.
    """

    name = "syntax"
    priority = 40

    PYTHON_SUFFIXES = {
        ".py",
        ".pyi",
    }

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        for entry in request.patch.get("files", []):

            path = str(entry.get("path", ""))

            if not any(path.endswith(ext) for ext in self.PYTHON_SUFFIXES):
                continue

            content = entry.get("content")

            if not isinstance(content, str):
                continue

            try:
                ast.parse(content, filename=path)

            except SyntaxError as exc:

                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        line=exc.lineno or 0,
                        column=exc.offset or 0,
                        message=exc.msg,
                        code="SYNTAX001",
                        suggestion="Fix the syntax error before applying the patch.",
                    )
                )

            except Exception as exc:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.CRITICAL,
                        file=path,
                        message=str(exc),
                        code="SYNTAX999",
                    )
                )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)
