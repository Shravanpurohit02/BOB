from dataclasses import dataclass, field
from typing import Any

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
    artifacts: list[GeneratedArtifact] = field(default_factory=list)

    generated_files: list[str] = field(default_factory=list)

    modified_files: list[str] = field(default_factory=list)

    created_directories: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    elapsed: float = 0.0

    #
    # Production execution integration
    #
    # Populated by the orchestrator after generated artifacts
    # have been adapted into engineering operations and executed.
    #
    execution: Any = None

    artifact_adaptation: Any = None
