from __future__ import annotations

import ast
from collections import defaultdict

from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class DuplicateValidator(BaseValidator):
    """
    Detect duplicate top-level classes, functions and assignments
    introduced by a generated patch.
    """

    name = "duplicates"
    priority = 60

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

        symbols: dict[str, list[tuple[str, int]]] = defaultdict(list)

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
                continue

            for node in tree.body:

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols[f"function:{node.name}"].append(
                        (path, node.lineno)
                    )

                elif isinstance(node, ast.ClassDef):
                    symbols[f"class:{node.name}"].append(
                        (path, node.lineno)
                    )

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols[f"variable:{target.id}"].append(
                                (path, node.lineno)
                            )

                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        symbols[f"variable:{node.target.id}"].append(
                            (path, node.lineno)
                        )

        for symbol, locations in symbols.items():

            if len(locations) < 2:
                continue

            for path, line in locations:

                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        line=line,
                        message=f"Duplicate symbol '{symbol}'.",
                        code="DUPLICATE001",
                        suggestion="Rename or remove the duplicate symbol.",
                    )
                )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)
