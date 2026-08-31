from __future__ import annotations
from typing import ClassVar

import ast

from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class QualityValidator(BaseValidator):
    """
    Detects common non-production code patterns.
    """

    name = "quality"
    priority = 80

    PYTHON_SUFFIXES: ClassVar = {".py", ".pyi"}

    FORBIDDEN_TEXT: ClassVar = {
        "TODO": "TODO comment found.",
        "FIXME": "FIXME comment found.",
        "XXX": "XXX marker found.",
        "HACK": "HACK marker found.",
    }

    FORBIDDEN_CALLS: ClassVar = {
        "print",
        "breakpoint",
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

            source = entry.get("content")

            if not isinstance(source, str):
                continue

            for marker, message in self.FORBIDDEN_TEXT.items():
                if marker in source:
                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.WARNING,
                            file=path,
                            message=message,
                            code="QUALITY001",
                            suggestion="Remove development markers.",
                        )
                    )

            try:
                tree = ast.parse(source, filename=path)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Pass):
                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.WARNING,
                            file=path,
                            line=node.lineno,
                            column=node.col_offset,
                            message="Placeholder 'pass' statement found.",
                            code="QUALITY002",
                            suggestion="Replace placeholder implementation.",
                        )
                    )

                elif isinstance(node, ast.Call):
                    func = node.func

                    if isinstance(func, ast.Name):
                        if func.id in self.FORBIDDEN_CALLS:
                            issues.append(
                                ValidationIssue(
                                    validator=self.name,
                                    severity=Severity.WARNING,
                                    file=path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Call to '{func.id}()' found.",
                                    code="QUALITY003",
                                    suggestion="Remove debugging calls.",
                                )
                            )

                    elif isinstance(func, ast.Attribute):
                        if func.attr == "print":
                            issues.append(
                                ValidationIssue(
                                    validator=self.name,
                                    severity=Severity.WARNING,
                                    file=path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message="Attribute print() call found.",
                                    code="QUALITY004",
                                )
                            )

        result = ValidationResult.success(self.name)
        result.issues.extend(issues)
        return result