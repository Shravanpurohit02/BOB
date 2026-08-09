from __future__ import annotations

from typing import ClassVar

from .operation_types import OperationType


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

    def classify(
        self,
        query: str,
        *,
        has_files: bool = False,
        has_symbols: bool = False,
    ) -> OperationType:
        text = query.lower()

        if any(word in text for word in self.RENAME_WORDS):
            return OperationType.RENAME_SYMBOL

        if any(word in text for word in self.MOVE_WORDS):
            return OperationType.MOVE_FILE

        if any(word in text for word in self.DELETE_WORDS):
            # An explicit symbol/function/class target must be treated
            # as a symbol deletion even when the containing .py file
            # is mentioned.
            symbol_words = (
                "function",
                "method",
                "symbol",
                "class",
                "variable",
                "constant",
                "property",
            )

            if any(word in text for word in symbol_words):
                return OperationType.DELETE_SYMBOL

            if has_symbols:
                return OperationType.DELETE_SYMBOL

            if ".py" in text or "file" in text:
                return OperationType.DELETE_FILE

            return OperationType.DELETE_SYMBOL

        if any(word in text for word in self.CREATE_WORDS):
            # Adding a symbol to an existing/resolved file is an
            # insertion operation, not file creation.
            if has_files:
                return OperationType.INSERT_SYMBOL

            if ".py" in text or "file" in text:
                return OperationType.CREATE_FILE

            return OperationType.INSERT_SYMBOL

        if any(word in text for word in self.IMPORT_WORDS):
            return OperationType.UPDATE_IMPORTS

        # A file was resolved but no symbol was resolved.
        # This is a file-level modification, not a symbol replacement.
        if has_files and not has_symbols:
            return OperationType.MODIFY_FILE

        # Preserve symbol replacement semantics when a symbol
        # was actually resolved.
        return OperationType.REPLACE_SYMBOL


classifier = OperationClassifier()
