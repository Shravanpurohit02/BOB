from dataclasses import dataclass


@dataclass(slots=True)
class Risk:

    severity: str

    title: str

    description: str

    mitigation: str = ""
