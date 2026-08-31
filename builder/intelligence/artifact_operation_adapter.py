from __future__ import annotations

from dataclasses import dataclass, field

from .operation_types import OperationType


class ArtifactOperationError(ValueError):
    """Raised when a generated artifact cannot be mapped safely."""


@dataclass(slots=True)
class ArtifactMapping:
    file: str
    action: str
    operation: str
    content_length: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ArtifactAdaptationReport:
    mappings: list[ArtifactMapping] = field(
        default_factory=list,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    @property
    def success(self) -> bool:
        return not self.warnings


class ArtifactOperationAdapter:
    """
    Converts generated code artifacts into executable engineering
    operation metadata.

    The adapter performs no filesystem mutation.

    Responsibilities:

    GeneratedArtifact
        -> validate artifact
        -> match planned operation
        -> validate action
        -> attach generated content
        -> return execution-ready plan
    """

    ACTION_TO_OPERATIONS = {
        "create": {
            "create_file",
            "create_project",
        },
        "modify": {
            "modify_file",
            "replace_symbol",
            "insert_symbol",
            "delete_symbol",
            "rename_symbol",
        },
        "delete": {
            "delete_file",
        },
    }

    def adapt(
        self,
        plan,
        generation,
        *,
        write: bool = False,
    ) -> ArtifactAdaptationReport:
        """
        Attach generated artifact contents to the corresponding
        planned operations.

        ``write`` controls execution intent only. The adapter itself
        never writes files.
        """

        report = ArtifactAdaptationReport()

        artifacts = getattr(
            generation,
            "artifacts",
            None,
        )

        if not artifacts:
            raise ArtifactOperationError(
                "Generation produced no artifacts."
            )

        operations = getattr(
            plan,
            "operations",
            None,
        )

        if not operations:
            raise ArtifactOperationError(
                "Execution plan contains no operations."
            )

        # A project-level operation has no concrete file path yet.
        # The generated artifact set is the authoritative source for
        # the concrete files of the new project.
        project_operations = [
            operation
            for operation in operations
            if str(
                getattr(
                    operation.operation,
                    "value",
                    operation.operation,
                )
            ) == OperationType.CREATE_PROJECT.value
        ]

        if project_operations:
            if len(project_operations) != 1:
                raise ArtifactOperationError(
                    "Only one CREATE_PROJECT operation is supported "
                    "per generation request."
                )

            if len(operations) != 1:
                raise ArtifactOperationError(
                    "CREATE_PROJECT cannot be combined with other "
                    "planned operations."
                )

        operation_by_file = {}

        for operation in operations:
            operation_name = str(
                getattr(
                    operation.operation,
                    "value",
                    operation.operation,
                )
            )

            if operation_name == OperationType.CREATE_PROJECT.value:
                continue

            file = str(operation.file)

            if file in operation_by_file:
                raise ArtifactOperationError(
                    f"Multiple operations target the same file: {file}"
                )

            operation_by_file[file] = operation

        generated_files = []

        for artifact in artifacts:
            for generated_file in getattr(
                artifact,
                "files",
                [],
            ):
                generated_files.append(
                    generated_file
                )

        if not generated_files:
            raise ArtifactOperationError(
                "Generation artifacts contain no files."
            )

        seen_generated = set()

        for generated in generated_files:
            file = str(
                getattr(
                    generated,
                    "path",
                    "",
                )
            ).strip()

            action = str(
                getattr(
                    generated,
                    "action",
                    "",
                )
            ).strip().lower()

            content = getattr(
                generated,
                "content",
                "",
            )

            if not file:
                raise ArtifactOperationError(
                    "Generated artifact contains an empty file path."
                )

            if file in seen_generated:
                raise ArtifactOperationError(
                    f"Duplicate generated artifact: {file}"
                )

            seen_generated.add(file)

            operation = operation_by_file.get(file)

            if operation is None and project_operations:
                project_operation = project_operations[0]

                if action != "create":
                    raise ArtifactOperationError(
                        "CREATE_PROJECT generation may only produce "
                        f"create artifacts: {file}"
                    )

                project_operation = project_operations[0]

                from .change_executor import EditOperation, OperationStatus

                materialized = EditOperation(
                    order=len(plan.operations) + 1,
                    file=file,
                    operation=OperationType.CREATE_FILE.value,
                    symbols=[],
                    impacts=[],
                    status=OperationStatus.READY,
                    metadata={
                        "action": OperationType.CREATE_FILE.value,
                        "target_exists": False,
                        "project_creation": True,
                    },
                )

                plan.operations.append(materialized)
                operation_by_file[file] = materialized
                operation = materialized

            if operation is None:
                raise ArtifactOperationError(
                    f"Generated artifact is outside the engineering plan: {file}"
                )

            expected_operations = self.ACTION_TO_OPERATIONS.get(
                action
            )

            if expected_operations is None:
                raise ArtifactOperationError(
                    f"Unsupported generated artifact action "
                    f"{action!r} for {file}"
                )

            actual_operation = str(
                getattr(
                    operation.operation,
                    "value",
                    operation.operation,
                )
            )

            if actual_operation not in expected_operations:
                expected = ", ".join(
                    sorted(expected_operations)
                )

                raise ArtifactOperationError(
                    f"Artifact/operation mismatch for {file}: "
                    f"artifact={action}, "
                    f"planned={actual_operation}, "
                    f"expected one of={expected}"
                )

            if action in {"create", "modify"}:
                if not isinstance(content, str):
                    raise ArtifactOperationError(
                        f"Generated content must be text: {file}"
                    )

                operation.metadata["content"] = content

            elif action == "delete":
                operation.metadata["content"] = ""

            operation.metadata["artifact_action"] = action
            operation.metadata["artifact_path"] = file
            operation.metadata["content_length"] = len(content)
            operation.metadata["write"] = bool(write)

            report.mappings.append(
                ArtifactMapping(
                    file=file,
                    action=action,
                    operation=actual_operation,
                    content_length=len(content),
                    metadata={
                        "write": bool(write),
                    },
                )
            )

        # Every planned concrete operation must have a corresponding
        # generated artifact.
        mapped_files = {
            mapping.file
            for mapping in report.mappings
        }

        for operation in plan.operations:
            operation_name = str(
                getattr(
                    operation.operation,
                    "value",
                    operation.operation,
                )
            )

            # CREATE_PROJECT is a semantic planning operation only.
            # It has already been expanded into concrete CREATE_FILE
            # operations above and must never reach the filesystem
            # execution boundary.
            if operation_name == OperationType.CREATE_PROJECT.value:
                continue

            if operation.file not in mapped_files:
                raise ArtifactOperationError(
                    "Generation did not produce an artifact for "
                    f"planned operation: {operation.file}"
                )

        # CREATE_PROJECT has served its purpose as the semantic
        # generation boundary. Remove it only after every generated
        # artifact has been successfully validated and materialized.
        if project_operations:
            plan.operations = [
                operation
                for operation in plan.operations
                if str(
                    getattr(
                        operation.operation,
                        "value",
                        operation.operation,
                    )
                ) != OperationType.CREATE_PROJECT.value
            ]

        return report


artifact_operation_adapter = ArtifactOperationAdapter()


__all__ = (
    "ArtifactMapping",
    "ArtifactAdaptationReport",
    "ArtifactOperationAdapter",
    "ArtifactOperationError",
    "artifact_operation_adapter",
)
