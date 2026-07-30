from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from builder.engineering.transaction.context import TransactionContext

if TYPE_CHECKING:
    from builder.execution.snapshot.models import ExecutionSnapshot
from uuid import uuid4

@dataclass(slots=True)
class ExecutionContext:
    id: str = field(default_factory=lambda: uuid4().hex)

    objective: str = ""
    workspace: str = "."

    plan_id: str = ""
    worker_id: str = ""
    job_id: str = ""

    metadata: dict = field(default_factory=dict)

    transaction: TransactionContext | None = None

    snapshot: ExecutionSnapshot | None = None

    options: dict = field(default_factory=dict)
