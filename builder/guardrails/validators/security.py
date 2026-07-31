from __future__ import annotations

import ast
import re

from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class SecurityValidator(BaseValidator):
    """
    Detects common security issues in generated source code.
    """

    name = "security"
    priority = 90

    PYTHON_SUFFIXES = {".py", ".pyi"}

    SECRET_PATTERNS = [
        (
            "SEC001",
            re.compile(
                r"(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]+['\"]",
                re.IGNORECASE,
            ),
            "Possible hardcoded secret detected.",
        ),
    ]

    DANGEROUS_CALLS = {
        ("os", "system"),
        ("os", "popen"),
        ("subprocess", "Popen"),
        ("subprocess", "call"),
        ("subprocess", "run"),
        ("subprocess", "check_call"),
        ("subprocess", "check_output"),
    }

    DANGEROUS_BUILTINS = {
        "eval",
        "exec",
        "compile",
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

            # Hardcoded secret detection
            for code, pattern, message in self.SECRET_PATTERNS:
                for match in pattern.finditer(source):
                    line = source.count("\n", 0, match.start()) + 1

                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.CRITICAL,
                            file=path,
                            line=line,
                            message=message,
                            code=code,
                            suggestion="Use environment variables or a secure secret manager.",
                        )
                    )

            try:
                tree = ast.parse(source, filename=path)
            except SyntaxError:
                continue

            for node in ast.walk(tree):

                if not isinstance(node, ast.Call):
                    continue

                # eval(), exec(), compile()
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_BUILTINS:
                        issues.append(
                            ValidationIssue(
                                validator=self.name,
                                severity=Severity.ERROR,
                                file=path,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Use of {node.func.id}().",
                                code="SEC010",
                                suggestion="Avoid dynamic code execution.",
                            )
                        )

                # os.system(), subprocess.run(), etc.
                elif isinstance(node.func, ast.Attribute):

                    if isinstance(node.func.value, ast.Name):

                        key = (
                            node.func.value.id,
                            node.func.attr,
                        )

                        if key in self.DANGEROUS_CALLS:

                            severity = Severity.ERROR

                            if key in {
                                ("os", "system"),
                                ("os", "popen"),
                            }:
                                severity = Severity.CRITICAL

                            issues.append(
                                ValidationIssue(
                                    validator=self.name,
                                    severity=severity,
                                    file=path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Use of {key[0]}.{key[1]}().",
                                    code="SEC020",
                                    suggestion=(
                                        "Avoid shell execution unless explicitly requested."
                                    ),
                                )
                            )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)
