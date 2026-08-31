
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath

ALLOWED_ACTIONS = {
    "create",
    "modify",
    "delete",
    "rename",
    "move",
}


@dataclass(slots=True)
class SemanticValidationResult:
    valid: bool
    reason: str = ""


class SemanticValidator:
    def validate(self, obj: dict) -> SemanticValidationResult:

        if not isinstance(obj, dict):
            return SemanticValidationResult(False, "root_not_object")

        seen = set()

        for file in obj.get("files", []):
            path = file.get("path", "")
            action = file.get("action", "modify")
            content = file.get("content")

            if not path:
                return SemanticValidationResult(False, "empty_path")

            p = PurePosixPath(path)

            if p.is_absolute():
                return SemanticValidationResult(False, "absolute_path")

            if ".." in p.parts:
                return SemanticValidationResult(False, "path_traversal")

            if path in seen:
                return SemanticValidationResult(False, "duplicate_path")

            seen.add(path)

            if action not in ALLOWED_ACTIONS:
                return SemanticValidationResult(
                    False,
                    f"unsupported_action:{action}",
                )

            if not isinstance(content, str):
                return SemanticValidationResult(
                    False,
                    "content_not_string",
                )

        for directory in obj.get("directories", []):
            path = directory.get("path", "")

            if not path:
                return SemanticValidationResult(
                    False,
                    "empty_directory_path",
                )

            p = PurePosixPath(path)

            if p.is_absolute():
                return SemanticValidationResult(
                    False,
                    "absolute_directory",
                )

            if ".." in p.parts:
                return SemanticValidationResult(
                    False,
                    "directory_traversal",
                )

        return SemanticValidationResult(True)


semantic_validator = SemanticValidator()
