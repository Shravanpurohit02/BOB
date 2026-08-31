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


class ImportValidator(BaseValidator):
    """
    Validates import statements in generated Python files.

    Performs static validation only.
    No code is imported or executed.
    """

    name = "imports"
    priority = 50

    PYTHON_SUFFIXES: ClassVar = {
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
                tree = ast.parse(content, filename=path)

            except SyntaxError:
                # Syntax validator reports this.
                continue

            imported: set[str] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name.strip()

                        if name in imported:
                            issues.append(
                                ValidationIssue(
                                    validator=self.name,
                                    severity=Severity.WARNING,
                                    file=path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Duplicate import '{name}'.",
                                    code="IMPORT001",
                                )
                            )

                        imported.add(name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""

                    if node.level < 0:
                        issues.append(
                            ValidationIssue(
                                validator=self.name,
                                severity=Severity.ERROR,
                                file=path,
                                line=node.lineno,
                                column=node.col_offset,
                                message="Invalid relative import.",
                                code="IMPORT002",
                            )
                        )

                    key = f"{'.' * node.level}{module}"

                    if key in imported:
                        issues.append(
                            ValidationIssue(
                                validator=self.name,
                                severity=Severity.WARNING,
                                file=path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Duplicate import '{key}'.",
                                code="IMPORT003",
                            )
                        )

                    imported.add(key)

        if issues:
            severity_order = {
                Severity.INFO: 0,
                Severity.WARNING: 1,
                Severity.ERROR: 2,
                Severity.CRITICAL: 3,
            }

            status = (
                ValidationResult.failure
                if any(
                    severity_order[i.severity] >= severity_order[Severity.ERROR]
                    for i in issues
                )
                else ValidationResult.success
            )

            if status is ValidationResult.success:
                result = ValidationResult.success(self.name)
                result.issues.extend(issues)
                return result

            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)