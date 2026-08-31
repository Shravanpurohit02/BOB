from __future__ import annotations

import tempfile
from pathlib import Path

from builder.codegen.autonomous_validator import AutonomousCodeValidator
from builder.guardrails.config import GuardrailConfig
from builder.guardrails.constants import SCHEMA_VERSION
from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationRequest,
)
from builder.guardrails.validators.api import APIValidator
from builder.guardrails.validators.files import FileValidator
from builder.guardrails.validators.imports import ImportValidator
from builder.guardrails.validators.path import PathValidator
from builder.guardrails.validators.schema import SchemaValidator
from builder.guardrails.validators.security import SecurityValidator
from builder.guardrails.validators.syntax import SyntaxValidator


NAME = "Validation Pipeline Contract"
CATEGORY = "Validation"
DESCRIPTION = (
    "Validates schema, path, file, syntax, import, security, API "
    "preservation, configuration and autonomous validation contracts."
)


def _request(
    files,
    *,
    workspace: Path | None = None,
    version: str = SCHEMA_VERSION,
):
    return ValidationRequest(
        workspace=workspace or Path("."),
        patch={
            "version": version,
            "files": files,
        },
    )


def run() -> bool:
    try:
        context = ValidationContext()

        # --------------------------------------------------------------
        # 1. Schema validator accepts a canonical patch.
        # --------------------------------------------------------------
        schema = SchemaValidator()

        valid_patch = _request(
            [
                {
                    "path": "app.py",
                    "operation": "create",
                    "content": "def main():\n    return 1\n",
                }
            ]
        )

        result = schema.validate(valid_patch, context)

        if result.failed or result.issues:
            return False

        # --------------------------------------------------------------
        # 2. Schema validator rejects malformed top-level schema.
        # --------------------------------------------------------------
        malformed = ValidationRequest(
            workspace=Path("."),
            patch={
                "files": [],
            },
        )

        result = schema.validate(malformed, context)

        if result.passed:
            return False

        if "SCHEMA002" not in {issue.code for issue in result.issues}:
            return False

        # --------------------------------------------------------------
        # 3. Schema validator rejects duplicate paths.
        # --------------------------------------------------------------
        duplicate = _request(
            [
                {
                    "path": "app.py",
                    "operation": "create",
                    "content": "x = 1\n",
                },
                {
                    "path": "app.py",
                    "operation": "modify",
                    "content": "x = 2\n",
                },
            ]
        )

        result = schema.validate(duplicate, context)

        if "SCHEMA008" not in {issue.code for issue in result.issues}:
            return False

        # --------------------------------------------------------------
        # 4. Path validator rejects traversal and absolute paths.
        # --------------------------------------------------------------
        path_validator = PathValidator()

        traversal = _request(
            [
                {
                    "path": "../escape.py",
                    "operation": "create",
                    "content": "x = 1\n",
                }
            ]
        )

        result = path_validator.validate(traversal, context)

        if "PATH002" not in {issue.code for issue in result.issues}:
            return False

        absolute = _request(
            [
                {
                    "path": "/tmp/escape.py",
                    "operation": "create",
                    "content": "x = 1\n",
                }
            ]
        )

        result = path_validator.validate(absolute, context)

        if "PATH001" not in {issue.code for issue in result.issues}:
            return False

        # --------------------------------------------------------------
        # 5. File validator rejects forbidden artifacts and binary data.
        # --------------------------------------------------------------
        file_validator = FileValidator()

        forbidden = _request(
            [
                {
                    "path": ".DS_Store",
                    "operation": "create",
                    "content": "forbidden artifact\n",
                }
            ]
        )

        result = file_validator.validate(forbidden, context)

        if "FILE001" not in {issue.code for issue in result.issues}:
            return False

        binary = _request(
            [
                {
                    "path": "data.txt",
                    "operation": "create",
                    "content": "safe\x00unsafe",
                }
            ]
        )

        result = file_validator.validate(binary, context)

        if "FILE005" not in {issue.code for issue in result.issues}:
            return False

        # --------------------------------------------------------------
        # 6. Syntax validator detects invalid Python.
        # --------------------------------------------------------------
        syntax = SyntaxValidator()

        invalid_python = _request(
            [
                {
                    "path": "broken.py",
                    "operation": "create",
                    "content": "def broken(:\n    pass\n",
                }
            ]
        )

        result = syntax.validate(invalid_python, context)

        if "SYNTAX001" not in {issue.code for issue in result.issues}:
            return False

        # --------------------------------------------------------------
        # 7. Import validator detects duplicate imports.
        # --------------------------------------------------------------
        imports = ImportValidator()

        duplicate_imports = _request(
            [
                {
                    "path": "imports.py",
                    "operation": "create",
                    "content": (
                        "import os\n"
                        "import os\n"
                    ),
                }
            ]
        )

        result = imports.validate(duplicate_imports, context)

        if "IMPORT001" not in {issue.code for issue in result.issues}:
            return False

        if result.failed:
            return False

        # --------------------------------------------------------------
        # 8. Security validator detects hardcoded secrets and dangerous
        #    execution.
        # --------------------------------------------------------------
        security = SecurityValidator()

        insecure = _request(
            [
                {
                    "path": "security.py",
                    "operation": "create",
                    "content": (
                        "api_key = 'hardcoded-secret'\n"
                        "eval('1 + 1')\n"
                        "import os\n"
                        "os.system('echo test')\n"
                    ),
                }
            ]
        )

        result = security.validate(insecure, context)

        codes = {issue.code for issue in result.issues}

        if "SEC001" not in codes:
            return False

        if "SEC010" not in codes:
            return False

        if "SEC020" not in codes:
            return False

        if not any(
            issue.severity is Severity.CRITICAL
            for issue in result.issues
        ):
            return False

        # --------------------------------------------------------------
        # 9. API validator detects removal of a public function/class.
        # --------------------------------------------------------------
        api = APIValidator()

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)

            target = workspace / "module.py"

            target.write_text(
                (
                    "def public_function():\n"
                    "    return 1\n"
                    "\n"
                    "class PublicClass:\n"
                    "    pass\n"
                    "\n"
                    "def _private():\n"
                    "    return 2\n"
                ),
                encoding="utf-8",
            )

            modification = _request(
                [
                    {
                        "path": "module.py",
                        "operation": "modify",
                        "content": (
                            "def public_function():\n"
                            "    return 1\n"
                        ),
                    }
                ],
                workspace=workspace,
            )

            result = api.validate(modification, context)

            if "API001" not in {issue.code for issue in result.issues}:
                return False

            if not any(
                "class:PublicClass" in issue.message
                for issue in result.issues
            ):
                return False

        # --------------------------------------------------------------
        # 10. Guardrail configuration must control validator state.
        # --------------------------------------------------------------
        config = GuardrailConfig()

        if not config.is_enabled("syntax"):
            return False

        config.disable("syntax")

        if config.is_enabled("syntax"):
            return False

        config.enable("syntax")

        if not config.is_enabled("syntax"):
            return False

        config.set_report_only("security", True)

        if not config.get("security").report_only:
            return False

        config.set_severity("security", Severity.CRITICAL)

        if config.get("security").severity is not Severity.CRITICAL:
            return False

        # --------------------------------------------------------------
        # 11. Autonomous validator checks required output structure.
        # --------------------------------------------------------------
        autonomous = AutonomousCodeValidator()

        outputs = [
            {
                "file": "app.py",
                "mode": "create",
                "generated": True,
                "patch": {},
            },
            {
                "file": "broken.py",
                "mode": "modify",
                "generated": True,
            },
        ]

        results = autonomous.validate(outputs)

        if len(results) != 2:
            return False

        if not results[0]["passed"]:
            return False

        if results[1]["passed"]:
            return False

        summary = autonomous.summary(results)

        if summary["total"] != 2:
            return False

        if summary["passed"] != 1:
            return False

        if summary["failed"] != 1:
            return False

        if summary["success"]:
            return False

        # --------------------------------------------------------------
        # 12. Clean pipeline input remains clean across core validators.
        # --------------------------------------------------------------
        clean = _request(
            [
                {
                    "path": "clean.py",
                    "operation": "create",
                    "content": (
                        "def main():\n"
                        "    return 1\n"
                    ),
                }
            ]
        )

        validators = (
            schema,
            path_validator,
            file_validator,
            syntax,
            imports,
            security,
        )

        for validator in validators:
            result = validator.validate(clean, context)

            if result.failed:
                return False

            if result.issues:
                return False

        return True

    except Exception:
        return False


__all__ = (
    "NAME",
    "CATEGORY",
    "DESCRIPTION",
    "run",
)
