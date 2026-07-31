from __future__ import annotations

import ast
from pathlib import Path

from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class APIValidator(BaseValidator):
    """
    Detect accidental removal of public APIs.

    Public APIs are:
    - top-level classes
    - top-level functions
    whose names do not begin with '_'
    """

    name = "api"
    priority = 70

    PYTHON_SUFFIXES = {".py", ".pyi"}

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        for file_patch in request.patch.get("files", []):

            operation = file_patch.get("operation")

            if operation != "modify":
                continue

            path = Path(file_patch.get("path", ""))

            if path.suffix not in self.PYTHON_SUFFIXES:
                continue

            repo_file = request.workspace / path

            if not repo_file.exists():
                continue

            try:
                old_source = repo_file.read_text(
                    encoding="utf-8"
                )
            except Exception:
                continue

            new_source = file_patch.get("content")

            if not isinstance(new_source, str):
                continue

            try:
                old_tree = ast.parse(
                    old_source,
                    filename=str(path),
                )
                new_tree = ast.parse(
                    new_source,
                    filename=str(path),
                )
            except SyntaxError:
                continue

            old_api = self._public_api(old_tree)
            new_api = self._public_api(new_tree)

            removed = old_api - new_api

            for symbol in sorted(removed):

                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=str(path),
                        message=(
                            f"Public API '{symbol}' "
                            "was removed."
                        ),
                        code="API001",
                        suggestion=(
                            "Preserve existing public APIs "
                            "unless explicitly requested."
                        ),
                    )
                )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)

    @staticmethod
    def _public_api(tree: ast.AST) -> set[str]:

        api: set[str] = set()

        for node in tree.body:

            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                if not node.name.startswith("_"):
                    api.add(f"function:{node.name}")

            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    api.add(f"class:{node.name}")

        return api
