from dataclasses import dataclass, field


@dataclass(slots=True)
class CodeGenerationRequest:
    instruction: str
    language: str = "python"
    context: str = ""
    model: str = ""

    workspace: str = "."
    overwrite: bool = False

    metadata: dict = field(default_factory=dict)
