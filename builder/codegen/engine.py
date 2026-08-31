import time
from pathlib import Path

from builder.codegen.generator import generator
from builder.codegen.parser import cleaner, extractor
from builder.codegen.request import CodeGenerationRequest
from builder.codegen.response import CodeGenerationResponse


class CodeEngine:
    def generate(
        self,
        request=None,
        *,
        objective=None,
        workspace=".",
        context=None,
        overwrite=False,
        language="python",
        model="",
    ):

        if isinstance(request, CodeGenerationRequest):
            req = request
        else:
            if objective is None:
                raise ValueError("objective or CodeGenerationRequest required")

            workspace = str(Path(workspace).resolve())

            if not Path(workspace).exists():
                raise FileNotFoundError(workspace)

            req = CodeGenerationRequest(
                instruction=objective,
                language=language,
                context=context or "",
                model=model,
                workspace=workspace,
                overwrite=overwrite,
            )

        started = time.perf_counter()

        result = generator.generate(req)

        code = cleaner.clean(extractor.code(result.text))


        artifacts = extractor.artifacts(result.text)

        self._validate_generation(
            req,
            artifacts,
        )

        generated_files = []
        modified_files = []
        created_directories = []

        for artifact in artifacts:
            for directory in artifact.directories:
                created_directories.append(directory.path)

            for file in artifact.files:
                if file.action == "create":
                    generated_files.append(file.path)
                else:
                    modified_files.append(file.path)

        return CodeGenerationResponse(
            success=result.success,
            provider=result.provider,
            model=result.model,
            code=code,
            raw=result.raw,
            artifacts=artifacts,
            generated_files=generated_files,
            modified_files=modified_files,
            created_directories=created_directories,
            warnings=[],
            errors=[],
            elapsed=round(
                time.perf_counter() - started,
                6,
            ),
        )


    def _validate_generation(
        self,
        request,
        artifacts,
    ):
        """
        Validate generated artifacts against the engineering plan.

        The generator is never allowed to change the semantic operation
        selected by the engineering planner.
        """

        allowed = set(request.resolved_files)

        operation_names = {
            str(
                getattr(
                    op,
                    "operation",
                    "",
                )
            ).lower()
            for op in request.operations
        }

        project_creation = (
            "create_project" in operation_names
        )

        # CREATE_PROJECT is a semantic project-root operation.
        # It deliberately does not resolve concrete files before
        # generation. Generated artifacts therefore become the
        # concrete file set, subject to workspace-boundary validation.
        workspace_root = Path(
            request.workspace
        ).resolve()

        workspace_name = workspace_root.name

        print("=" * 80)
        print("PLANNED OPERATIONS")
        print("=" * 80)

        for name in sorted(operation_names):
            print(name)

        print("=" * 80)

        action_requirements = {
            "create_file": {"create"},
            "modify_file": {"modify"},
            "replace_symbol": {"modify"},
            "insert_symbol": {"modify"},
            # Symbol deletion modifies the containing file.
            # Only delete_file removes the filesystem object itself.
            "delete_symbol": {"modify"},
            "delete_file": {"delete"},
            "rename_symbol": {"modify"},
            "rename_file": {"rename"},
            "move_file": {"move"},
        }

        allowed_actions = set()

        for operation in operation_names:
            allowed_actions.update(
                action_requirements.get(operation, set())
            )

        for artifact in artifacts:
            for file in artifact.files:

                # All generated artifact paths are workspace-relative.
                # Absolute paths are never permitted.
                raw_path = str(
                    file.path
                ).strip()

                if not raw_path:
                    raise ValueError(
                        "Generator returned an empty artifact path."
                    )

                candidate = Path(raw_path)

                if candidate.is_absolute():
                    raise ValueError(
                        "Generator returned an absolute artifact path: "
                        f"{raw_path}"
                    )

                # Some models incorrectly echo the temporary workspace
                # directory name. Since that directory is the actual
                # execution root, normalize only that exact leading
                # component. Do not normalize arbitrary path prefixes.
                parts = candidate.parts

                if (
                    project_creation
                    and parts
                    and parts[0] == workspace_name
                ):
                    normalized = Path(
                        *parts[1:]
                    )

                    if not normalized.parts:
                        raise ValueError(
                            "Generator returned the workspace root "
                            "as a file artifact."
                        )

                    file.path = normalized.as_posix()
                else:
                    file.path = candidate.as_posix()

                normalized_path = (
                    workspace_root / file.path
                ).resolve()

                try:
                    normalized_path.relative_to(
                        workspace_root
                    )
                except ValueError as exc:
                    raise ValueError(
                        "Generator attempted to escape the workspace: "
                        f"{file.path}"
                    ) from exc

                if (
                    not project_creation
                    and allowed
                    and file.path not in allowed
                ):
                    raise ValueError(
                        "Generator attempted unauthorized file: "
                        f"{file.path}"
                    )

                action = str(
                    file.action
                ).strip().lower()

                if action not in {
                    "create",
                    "modify",
                    "delete",
                    "rename",
                    "move",
                }:
                    raise ValueError(
                        f"Generator returned unsupported action "
                        f"{action!r} for {file.path}"
                    )

                if (
                    allowed_actions
                    and action not in allowed_actions
                ):
                    expected = ", ".join(
                        sorted(allowed_actions)
                    )

                    raise ValueError(
                        "Generator action does not match the "
                        f"engineering operation for {file.path}: "
                        f"received={action!r}, "
                        f"expected one of={expected!r}, "
                        f"operations={sorted(operation_names)!r}"
                    )

                if (
                    action == "create"
                    and file.path in allowed
                    and not project_creation
                    and "create_file" not in operation_names
                ):
                    raise ValueError(
                        "Generator attempted to create an existing "
                        "planned target without a create_file "
                        f"operation: {file.path}"
                    )



engine = CodeEngine()
