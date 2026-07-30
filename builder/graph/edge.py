from dataclasses import dataclass

@dataclass(slots=True)
class Edge:
    source: str
    target: str
    relation: str = "depends_on"
