from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceSpan:
    """
    Character offsets for a source fragment.
    """

    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start


class SourceSpanResolver:
    """
    Converts AST line/column coordinates into character spans.
    """

    @staticmethod
    def offset(
        source: str,
        line: int,
        column: int,
    ) -> int:

        lines = source.splitlines(keepends=True)

        if line < 1 or line > len(lines):
            raise ValueError("Invalid line number.")

        return (
            sum(len(lines[i]) for i in range(line - 1))
            + column
        )


    @staticmethod
    def identifier_span(
        source: str,
        line: int,
        name: str,
    ) -> SourceSpan:
        """
        Locate an identifier on a given source line and return its
        character span.
        """

        lines = source.splitlines(keepends=True)

        if line < 1 or line > len(lines):
            raise ValueError("Invalid line number.")

        text = lines[line - 1]

        column = text.find(name)

        if column < 0:
            raise ValueError(f"Identifier '{name}' not found.")

        start = SourceSpanResolver.offset(
            source,
            line,
            column,
        )

        return SourceSpan(
            start=start,
            end=start + len(name),
        )


source_span_resolver = SourceSpanResolver()

__all__ = (
    "SourceSpan",
    "SourceSpanResolver",
    "source_span_resolver",
)
