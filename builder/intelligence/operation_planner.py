from dataclasses import dataclass, field
from enum import Enum

from .edit_session import edit_session_builder


class OperationType(str, Enum):
    REPLACE_SYMBOL = "replace_symbol"
    INSERT_SYMBOL = "insert_symbol"
    DELETE_SYMBOL = "delete_symbol"
    RENAME_SYMBOL = "rename_symbol"

    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    RENAME_FILE = "rename_file"
    MOVE_FILE = "move_file"

    UPDATE_IMPORTS = "update_imports"


@dataclass(slots=True)
class PlannedOperation:
    file: str

    operation: OperationType

    symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class OperationPlan:
    query: str
    risk: str

    operations: list[PlannedOperation] = field(default_factory=list)


class OperationPlanner:

    def build(
        self,
        workspace: str,
    ):
        edit_session_builder.build(workspace)

    def plan(
        self,
        query: str,
    ):

        session = edit_session_builder.create(query)

        plan = OperationPlan(
            query=query,
            risk=session.risk,
        )

        for target in session.targets:

            action = target.metadata.get(
                "action",
                OperationType.REPLACE_SYMBOL.value,
            )

            try:
                operation = OperationType(action)
            except ValueError:
                operation = OperationType.REPLACE_SYMBOL

            plan.operations.append(
                PlannedOperation(
                    file=target.file,
                    operation=operation,
                    symbols=list(target.symbols),
                    impacts=list(target.impacts),
                    metadata=dict(target.metadata),
                )
            )

        return plan


operation_planner = OperationPlanner()
