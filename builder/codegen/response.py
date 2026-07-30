from dataclasses import dataclass, field

from builder.codegen.artifacts import (
    GeneratedArtifact,
)


@dataclass(slots=True)
class CodeGenerationResponse:

    success: bool

    provider: str = ""

    model: str = ""

    #
    # Legacy single-file output
    #
    code: str = ""

    #
    # Raw provider response
    #
    raw: dict = field(default_factory=dict)

    #
    # Code Generation V2
    #
    artifacts: list[GeneratedArtifact] = field(
        default_factory=list
    )

    generated_files: list[str] = field(
        default_factory=list
    )

    modified_files: list[str] = field(
        default_factory=list
    )

    created_directories: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    elapsed: float = 0.0
