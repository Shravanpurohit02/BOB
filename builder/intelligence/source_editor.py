from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EditResult:
    success: bool
    before: str
    after: str
    message: str


class SourceEditor:
    """
    Pure source editing primitives.

    No filesystem.
    No AST.
    No transactions.
    No patch engine.
    """

    def replace_range(
        self,
        source: str,
        start: int,
        end: int,
        replacement: str,
    ) -> EditResult:

        if (
            start < 0
            or end < start
            or end > len(source)
        ):
            return EditResult(
                success=False,
                before=source,
                after=source,
                message="Invalid edit range.",
            )

        updated = (
            source[:start]
            + replacement
            + source[end:]
        )

        return EditResult(
            success=True,
            before=source,
            after=updated,
            message="Range replaced.",
        )


    def delete_range(
        self,
        source: str,
        start: int,
        end: int,
    ) -> EditResult:
        return self.replace_range(
            source=source,
            start=start,
            end=end,
            replacement="",
        )

    def insert_before(
        self,
        source: str,
        offset: int,
        text: str,
    ) -> EditResult:
        return self.replace_range(
            source=source,
            start=offset,
            end=offset,
            replacement=text,
        )

    def insert_after(
        self,
        source: str,
        offset: int,
        text: str,
    ) -> EditResult:
        return self.replace_range(
            source=source,
            start=offset,
            end=offset,
            replacement=text,
        )


    def replace_text(
        self,
        source: str,
        old: str,
        new: str,
        *,
        count: int = 1,
    ) -> EditResult:
        """
        Replace occurrences of literal text.

        This primitive is intended for deterministic source-to-source
        transformations where an AST rewrite is unnecessary.
        """

        if not old:
            return EditResult(
                success=False,
                before=source,
                after=source,
                message="Search text is empty.",
            )

        occurrences = source.count(old)

        if occurrences == 0:
            return EditResult(
                success=False,
                before=source,
                after=source,
                message="Search text not found.",
            )

        if count < 0:
            updated = source.replace(old, new)
        else:
            updated = source.replace(old, new, count)

        return EditResult(
            success=True,
            before=source,
            after=updated,
            message="Text replaced.",
        )

    def rename_identifier(
        self,
        source: str,
        start: int,
        end: int,
        new_name: str,
    ) -> EditResult:
        return self.replace_range(
            source=source,
            start=start,
            end=end,
            replacement=new_name,
        )


source_editor = SourceEditor()

__all__ = (
    "EditResult",
    "SourceEditor",
    "source_editor",
)
