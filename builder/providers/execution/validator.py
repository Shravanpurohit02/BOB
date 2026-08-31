
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
class ProviderValidationResult:
    valid: bool
    reason: str = ""


class ResponseValidator:
    SCHEMA = "vidhi-builder/v1"

    def validate(self, text: str) -> ProviderValidationResult:

        if not isinstance(text, str):
            return ProviderValidationResult(False, "response_not_string")

        text = text.strip()

        if not text:
            return ProviderValidationResult(False, "empty_response")

        try:
            text.encode("utf-8")
        except UnicodeError:
            return ProviderValidationResult(False, "invalid_utf8")

        try:
            obj = json.loads(text)
        except Exception:
            return ProviderValidationResult(False, "invalid_json")

        if not isinstance(obj, dict):
            return ProviderValidationResult(False, "root_not_object")

        if obj.get("schema") != self.SCHEMA:
            return ProviderValidationResult(False, "invalid_schema")

        missing = REQUIRED_KEYS - obj.keys()

        if missing:
            return ProviderValidationResult(
                False,
                f"missing_keys:{','.join(sorted(missing))}",
            )

        if not isinstance(obj["directories"], list):
            return ProviderValidationResult(False, "directories_not_list")

        if not isinstance(obj["files"], list):
            return ProviderValidationResult(False, "files_not_list")

        if not isinstance(obj["warnings"], list):
            return ProviderValidationResult(False, "warnings_not_list")

        for item in obj["directories"]:
            if not isinstance(item, dict):
                return ProviderValidationResult(False, "directory_not_object")

            if "path" not in item:
                return ProviderValidationResult(False, "directory_missing_path")

        for item in obj["files"]:
            if not isinstance(item, dict):
                return ProviderValidationResult(False, "file_not_object")

            for key in (
                "path",
                "content",
            ):
                if key not in item:
                    return ProviderValidationResult(
                        False,
                        f"file_missing_{key}",
                    )

        return ProviderValidationResult(True)


validator = ResponseValidator()
