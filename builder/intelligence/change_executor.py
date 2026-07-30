from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter

from .operation_planner import operation_planner


class OperationStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


@dataclass(slots=True)
class EditOperation:
    order: int

    file: str

    operation: str

    symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)

    status: OperationStatus = OperationStatus.PENDING

    patch_id: str = ""
    backup: str = ""

    started: float = 0.0
    finished: float = 0.0

    error: str = ""

    metadata: dict = field(default_factory=dict)

    @property
    def elapsed(self):
        if self.started == 0 or self.finished == 0:
            return 0.0
        return round(
            self.finished - self.started,
            6,
        )


@dataclass(slots=True)
class ChangeExecutionPlan:
    query: str
    risk: str

    operations: list[EditOperation] = field(
        default_factory=list
    )


@dataclass(slots=True)
class ExecutionReport:

    success: bool = False

    total: int = 0
    completed: int = 0
    failed: int = 0
    rolled_back: int = 0
    skipped: int = 0

    elapsed: float = 0.0

    operations: list[EditOperation] = field(
        default_factory=list
    )


class ChangeExecutor:

    def __init__(self):
        self._started = 0.0

    def build(
        self,
        workspace: str,
    ):
        operation_planner.build(workspace)

    def create_plan(
        self,
        query: str,
    ):

        op_plan = operation_planner.plan(query)

        plan = ChangeExecutionPlan(
            query=query,
            risk=op_plan.risk,
        )

        for order, op in enumerate(
            op_plan.operations,
            start=1,
        ):

            plan.operations.append(
                EditOperation(
                    order=order,
                    file=op.file,
                    operation=op.operation.value,
                    symbols=list(op.symbols),
                    impacts=list(op.impacts),
                    status=OperationStatus.READY,
                    metadata=dict(op.metadata),
                )
            )

        return plan

    def report(
        self,
        plan: ChangeExecutionPlan,
    ):

        report = ExecutionReport()

        report.operations = list(plan.operations)
        report.total = len(plan.operations)

        for op in plan.operations:

            if op.status is OperationStatus.COMPLETED:
                report.completed += 1

            elif op.status is OperationStatus.FAILED:
                report.failed += 1

            elif op.status is OperationStatus.ROLLED_BACK:
                report.rolled_back += 1

            elif op.status is OperationStatus.SKIPPED:
                report.skipped += 1

        report.success = (
            report.completed == report.total
            and report.failed == 0
        )

        report.elapsed = round(
            perf_counter() - self._started,
            6,
        )

        return report


change_executor = ChangeExecutor()
