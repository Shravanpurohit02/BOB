from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class ProjectEdge:
    """
    Directed relationship between two project nodes.
    """

    source: str

    target: str

    relationship: str = "imports"

    weight: float = 1.0

    metadata: dict = field(default_factory=dict)

    @property
    def key(
        self,
    ) -> tuple[str, str, str]:

        return (
            self.source,
            self.target,
            self.relationship,
        )

    def to_dict(
        self,
    ) -> dict:

        return asdict(self)


Edge = ProjectEdge
