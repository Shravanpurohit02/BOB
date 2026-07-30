from dataclasses import dataclass, field


@dataclass(slots=True)
class EngineeringContext:

    objective: str = ""

    workspace: str = ""

    target_modules: list[str] = field(default_factory=list)

    related_files: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)

    symbols: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
