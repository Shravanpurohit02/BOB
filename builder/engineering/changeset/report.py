from dataclasses import dataclass, field


@dataclass(slots=True)
class EngineeringReport:

    summary: str = ""

    recommendations: list[str] = field(default_factory=list)

    notes: list[str] = field(default_factory=list)
