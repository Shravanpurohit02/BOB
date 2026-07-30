import ast
from pathlib import Path

from builder.validation.result import ValidationResult


class PythonValidator:

    def validate(self, path: Path):

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
                    if any(n.startswith("frontend") for n in names):
                        return ValidationResult(
                            path=str(path),
                            success=False,
                            message="Backend cannot import frontend modules.",
                        )

                if "/frontend/" in path_str:
                    if any(n.startswith("backend") for n in names):
                        return ValidationResult(
                            path=str(path),
                            success=False,
                            message="Frontend cannot import backend modules.",
                        )

            return ValidationResult(
                path=str(path),
                success=True,
            )

        except Exception as exc:

            return ValidationResult(
                path=str(path),
                success=False,
                message=str(exc),
            )


validator = PythonValidator()
