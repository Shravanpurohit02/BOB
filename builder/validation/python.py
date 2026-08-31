import ast
from pathlib import Path

from builder.guardrails.models import (
    Severity,
    ValidationIssue,
    ValidationResult,
)


class PythonValidator:
    NAME = "python"

    def validate(
        self,
        path: Path,
    ) -> ValidationResult:

        try:
            source = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            tree = ast.parse(source)

            path_str = str(path).replace("\\", "/")

            for node in ast.walk(tree):

                if isinstance(node, ast.Import):
                    names = [n.name for n in node.names]

                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]

                else:
                    continue

                if "/backend/" in path_str:
                    if any(name.startswith("frontend") for name in names):
                        return ValidationResult.failure(
                            validator=self.NAME,
                            issues=[
                                ValidationIssue(
                                    validator=self.NAME,
                                    severity=Severity.ERROR,
                                    message="Backend cannot import frontend modules.",
                                    file=str(path),
                                    line=getattr(node, "lineno", 0),
                                    column=getattr(node, "col_offset", 0),
                                )
                            ],
                        )

                if "/frontend/" in path_str:
                    if any(name.startswith("backend") for name in names):
                        return ValidationResult.failure(
                            validator=self.NAME,
                            issues=[
                                ValidationIssue(
                                    validator=self.NAME,
                                    severity=Severity.ERROR,
                                    message="Frontend cannot import backend modules.",
                                    file=str(path),
                                    line=getattr(node, "lineno", 0),
                                    column=getattr(node, "col_offset", 0),
                                )
                            ],
                        )

            return ValidationResult.success(
                validator=self.NAME,
                metadata={
                    "file": str(path),
                },
            )

        except Exception as exc:
            return ValidationResult.failure(
                validator=self.NAME,
                issues=[
                    ValidationIssue(
                        validator=self.NAME,
                        severity=Severity.ERROR,
                        message=str(exc),
                        file=str(path),
                    )
                ],
            )


validator = PythonValidator()
