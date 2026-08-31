from __future__ import annotations

import json
from dataclasses import dataclass

REQUIRED_KEYS = {
    "schema",
    "directories",
    "files",
    "warnings",
}


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    reason: str = ""


class ResponseValidator:
    SCHEMA = "vidhi-builder/v1"

    def validate(self, text: str) -> ValidationResult:

        if not isinstance(text, str):
            return ValidationResult(False, "response_not_string")

        text = text.strip()

        if not text:
            return ValidationResult(False, "empty_response")

        try:
            text.encode("utf-8")
        except UnicodeError:
            return ValidationResult(False, "invalid_utf8")

        try:
            obj = json.loads(text)
        except Exception:
            return ValidationResult(False, "invalid_json")

        if not isinstance(obj, dict):
            return ValidationResult(False, "root_not_object")

        if obj.get("schema") != self.SCHEMA:
            return ValidationResult(False, "invalid_schema")

        missing = REQUIRED_KEYS - obj.keys()

        if missing:
            return ValidationResult(
                False,
                f"missing_keys:{','.join(sorted(missing))}",
            )

        if not isinstance(obj["directories"], list):
            return ValidationResult(False, "directories_not_list")

        if not isinstance(obj["files"], list):
            return ValidationResult(False, "files_not_list")

        if not isinstance(obj["warnings"], list):
            return ValidationResult(False, "warnings_not_list")

        for item in obj["directories"]:
            if not isinstance(item, dict):
                return ValidationResult(False, "directory_not_object")

            if "path" not in item:
                return ValidationResult(False, "directory_missing_path")

        for item in obj["files"]:
            if not isinstance(item, dict):
                return ValidationResult(False, "file_not_object")

            for key in (
                "path",
                "content",
            ):
                if key not in item:
                    return ValidationResult(
                        False,
                        f"file_missing_{key}",
                    )

        return ValidationResult(True)


validator = ResponseValidator()
