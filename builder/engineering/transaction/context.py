from __future__ import annotations

from dataclasses import dataclass, field

from .models import EngineeringTransaction


@dataclass(slots=True)
class TransactionContext:
    """
    Carries the active engineering transaction through the
    execution pipeline.

    The transaction is optional to preserve backward
    compatibility with existing callers.
    """

    transaction: EngineeringTransaction | None = None

    metadata: dict = field(default_factory=dict)

    def active(self) -> bool:
        return self.transaction is not None

    @property
    def id(self) -> str:
        if self.transaction is None:
            return ""
        return self.transaction.id
