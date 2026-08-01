from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EngineeringTask:
    id: str
    title: str
    objective: str
    priority: int = 1
    complexity: int = 1
    dependencies: list[str] = field(default_factory=list)


class TaskDecomposer:
    VERBS = (
        "create",
        "modify",
        "update",
        "fix",
        "repair",
        "delete",
        "remove",
        "rename",
        "move",
        "refactor",
        "optimize",
        "improve",
        "implement",
        "test",
        "review",
        "validate",
    )

    def decompose(
        self,
        objective: str,
    ) -> list[EngineeringTask]:

        text = objective.strip()

        parts = [
            p.strip()
            for p in text.replace(" then ", ",").replace(" and ", ",").split(",")
            if p.strip()
        ]

        tasks = []

        for index, part in enumerate(parts, start=1):
            complexity = max(
                1,
                min(
                    5,
                    len(part.split()) // 8 + 1,
                ),
            )

            tasks.append(
                EngineeringTask(
                    id=f"T{index:03d}",
                    title=part[:80],
                    objective=part,
                    priority=index,
                    complexity=complexity,
                )
            )

        return tasks


engine = TaskDecomposer()
