from __future__ import annotations

from dataclasses import dataclass, field

from builder.intelligence.reference_span import (
    ReferenceSpan,
    reference_span_indexer,
)


@dataclass(slots=True)
class ReferenceResolution:
    query: str

    exact: list[ReferenceSpan] = field(default_factory=list)
    module: list[ReferenceSpan] = field(default_factory=list)


class ReferenceResolver:
    def __init__(self):
        self.index = None

    def build(
        self,
        workspace: str,
    ):
        self.index = reference_span_indexer.build(workspace)

    def resolve(
        self,
        symbol: str,
        module: str | None = None,
    ) -> ReferenceResolution:

        result = ReferenceResolution(query=symbol)

        if self.index is None:
            return result

        for ref in self.index.references:

            if ref.symbol != symbol:
                continue

            result.exact.append(ref)

            if (
                module is not None
                and ref.module == module
            ):
                result.module.append(ref)

        return result


    def resolve_qualified(
        self,
        module: str,
        symbol: str,
    ) -> ReferenceResolution:
        """
        Resolve references using a fully-qualified symbol.
        """

        result = ReferenceResolution(
            query=f"{module}.{symbol}",
        )

        if self.index is None:
            return result

        for ref in self.index.references:

            if (
                ref.module == module
                and ref.symbol == symbol
            ):
                result.exact.append(ref)
                result.module.append(ref)

        return result


reference_resolver = ReferenceResolver()

__all__ = (
    "ReferenceResolution",
    "ReferenceResolver",
    "reference_resolver",
)
