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
                raise ValueError(
                    "objective or CodeGenerationRequest required"
                )

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

        code = cleaner.clean(
            extractor.code(result.text)
        )

        artifacts = extractor.artifacts(
            result.text
        )

        generated_files = []
        modified_files = []
        created_directories = []

        for artifact in artifacts:

            for directory in artifact.directories:
                created_directories.append(
                    directory.path
                )

            for file in artifact.files:

                if file.action == "create":
                    generated_files.append(
                        file.path
                    )
                else:
                    modified_files.append(
                        file.path
                    )

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


engine = CodeEngine()
