from dataclasses import dataclass, field


@dataclass(slots=True)
class RepositoryAnalysis:

    project: str = ""

    python_files: int = 0

    packages: int = 0

    modules: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)

    entrypoints: list[str] = field(default_factory=list)
