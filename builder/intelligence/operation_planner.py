from dataclasses import dataclass, field
import re
from pathlib import Path

from .edit_session import edit_session_builder
from .operation_types import OperationType
from .operation_classifier import classifier


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

    operations: list[PlannedOperation] = field(
        default_factory=list,
    )


class OperationPlanner:
    def __init__(self):
        self.workspace = "."

    def build(
        self,
        workspace: str,
    ):
        self.workspace = str(
            Path(workspace).resolve()
        )

        edit_session_builder.build(
            self.workspace
        )

    def _extract_create_target(
        self,
        query: str,
    ) -> str | None:
        """
        Resolve a filename from an explicit file-creation request.

        Supported forms include:

        create new_module.py
        create file new_module.py
        create a new file new_module.py
        generate new_module.py
        add file new_module.py
        new file new_module.py
        """

        text = query.strip()

        if not re.search(
            r'\b(create|add|generate|new)\b',
            text,
            re.IGNORECASE,
        ):
            return None

        patterns = (
            # create new_module.py
            r'\b(?:create|generate)\s+[`"]?([^`"\s,;]+\.py)[`"]?',

            # create file new_module.py
            r'\b(?:create|add|generate)\s+(?:a\s+)?(?:new\s+)?file\s+[`"]?([^`"\s,;]+)[`"]?',

            # create new_module.py that ...
            r'\b(?:create|add|generate)\s+[`"]?([^`"\s,;]+)[`"]?\s+(?:that|which|with|to)\b',

            # new file new_module.py
            r'\bnew\s+file\s+[`"]?([^`"\s,;]+)[`"]?',
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            candidate = match.group(1).strip()

            if not candidate:
                continue

            if not candidate.endswith(".py"):
                continue

            return candidate

        return None

    def _create_operation(
        self,
        query: str,
    ) -> PlannedOperation | None:
        """
        Build a CREATE_FILE operation when the requested target
        does not already exist.

        This does not create anything on disk. It only creates the
        engineering operation required by the downstream artifact
        and patch pipeline.
        """

        target = self._extract_create_target(
            query
        )

        if not target:
            return None

        workspace = Path(
            self.workspace
        ).resolve()

        candidate = (
            workspace / target
        ).resolve()

        try:
            candidate.relative_to(
                workspace
            )
        except ValueError:
            return None

        if candidate.exists():
            return None

        relative = candidate.relative_to(
            workspace
        ).as_posix()

        return PlannedOperation(
            file=relative,
            operation=OperationType.CREATE_FILE,
            symbols=[],
            impacts=[],
            metadata={
                "action": OperationType.CREATE_FILE.value,
                "symbol_count": 0,
                "impact_count": 0,
                "target_exists": False,
                "explicit_create": True,
            },
        )

    def plan(
        self,
        query: str,
    ):

        session = edit_session_builder.create(
            query
        )

        plan = OperationPlan(
            query=query,
            risk=session.risk,
        )

        for target in session.targets:
            operation = classifier.classify(
                query,
                has_files=True,
                has_symbols=bool(
                    target.symbols
                ),
            )

            target.metadata["action"] = (
                operation.value
            )

            plan.operations.append(
                PlannedOperation(
                    file=target.file,
                    operation=operation,
                    symbols=list(
                        target.symbols
                    ),
                    impacts=list(
                        target.impacts
                    ),
                    metadata=dict(
                        target.metadata
                    ),
                )
            )

        #
        # Existing-file planning remains unchanged.
        #
        # If no existing target was discovered, explicitly detect
        # a create-file request and synthesize the corresponding
        # engineering operation.
        #

        if not plan.operations:
            create_operation = (
                self._create_operation(query)
            )

            if create_operation is not None:
                plan.operations.append(
                    create_operation
                )

        return plan


operation_planner = OperationPlanner()
