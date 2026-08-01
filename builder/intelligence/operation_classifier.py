from __future__ import annotations

from typing import ClassVar

from .operation_planner import OperationType


class OperationClassifier:
    CREATE_WORDS: ClassVar[frozenset[str]] = frozenset({
        "create",
        "add",
        "generate",
        "new",
    })

    DELETE_WORDS: ClassVar[frozenset[str]] = frozenset({
        "delete",
        "remove",
    })

    RENAME_WORDS: ClassVar[frozenset[str]] = frozenset({
        "rename",
    })

    MOVE_WORDS: ClassVar[frozenset[str]] = frozenset({
        "move",
    })

    IMPORT_WORDS: ClassVar[frozenset[str]] = frozenset({
        "import",
        "imports",
    })

    def classify(self, query: str) -> OperationType:
        text = query.lower()

        if any(word in text for word in self.RENAME_WORDS):
            return OperationType.RENAME_SYMBOL

        if any(word in text for word in self.MOVE_WORDS):
            return OperationType.MOVE_FILE

        if any(word in text for word in self.DELETE_WORDS):
            if ".py" in text or "file" in text:
                return OperationType.DELETE_FILE
            return OperationType.DELETE_SYMBOL

        if any(word in text for word in self.CREATE_WORDS):
            if ".py" in text or "file" in text:
                return OperationType.CREATE_FILE
            return OperationType.INSERT_SYMBOL

        if any(word in text for word in self.IMPORT_WORDS):
            return OperationType.UPDATE_IMPORTS

        return OperationType.REPLACE_SYMBOL


classifier = OperationClassifier()
