from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class ProjectNode:
    """
    Node within the project dependency graph.
    """

    path: str

    name: str = ""

    kind: str = "module"

    imports: list[str] = field(default_factory=list)

    exports: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:

        if not self.name:
            self.name = self.path.rsplit("/", 1)[-1]

    def to_dict(self) -> dict:

        return asdict(self)


Node = ProjectNode
