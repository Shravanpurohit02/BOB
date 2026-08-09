from __future__ import annotations

from dataclasses import dataclass, field


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

        operation_by_file = {}

        for operation in operations:
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

        # Every planned operation must have a corresponding artifact.
        mapped_files = {
            mapping.file
            for mapping in report.mappings
        }

        for operation in operations:
            if operation.file not in mapped_files:
                raise ArtifactOperationError(
                    "Generation did not produce an artifact for "
                    f"planned operation: {operation.file}"
                )

        return report


artifact_operation_adapter = ArtifactOperationAdapter()


__all__ = (
    "ArtifactMapping",
    "ArtifactAdaptationReport",
    "ArtifactOperationAdapter",
    "ArtifactOperationError",
    "artifact_operation_adapter",
)
