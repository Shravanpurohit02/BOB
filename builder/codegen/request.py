from dataclasses import dataclass, field


@dataclass(slots=True)
class CodeGenerationRequest:
    instruction: str
    language: str = "python"
    context: str = ""
    model: str = ""

    workspace: str = "."
    overwrite: bool = False

    # ---------------------------------------------------------
    # Engineering Plan
    # ---------------------------------------------------------

    resolved_files: list[str] = field(default_factory=list)

    resolved_symbols: list = field(default_factory=list)

    operations: list = field(default_factory=list)

    execution_order: list[str] = field(default_factory=list)

    impacts: list = field(default_factory=list)

    risk: str = "low"


    metadata: dict = field(default_factory=dict)
