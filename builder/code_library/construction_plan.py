from __future__ import annotations

from dataclasses import dataclass

from .architecture_composition import (
    ArchitectureCompositionResult,
)


@dataclass(frozen=True)
class ConstructionStep:
    step_id: str
    order: int
    asset_id: str
    action: str
    dependencies: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.step_id.strip():
            raise ValueError("step_id must not be empty")

        if self.order < 1:
            raise ValueError("order must be >= 1")

        if not self.asset_id.strip():
            raise ValueError("asset_id must not be empty")

        if not self.action.strip():
            raise ValueError("action must not be empty")

        object.__setattr__(
            self,
            "dependencies",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.dependencies
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata or {}),
        )

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "order": self.order,
            "asset_id": self.asset_id,
            "action": self.action,
            "dependencies": list(self.dependencies),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class ConstructionPlanResult:
    requirement_name: str
    steps: tuple[ConstructionStep, ...]
    execution_order: tuple[str, ...]
    blocked_steps: tuple[str, ...]
    generated: bool
    executable: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "execution_order": list(
                self.execution_order
            ),
            "blocked_steps": list(
                self.blocked_steps
            ),
            "generated": self.generated,
            "executable": self.executable,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryConstructionPlanner:
    """
    Converts a validated CL-15.4 architecture into a deterministic
    construction plan suitable for downstream generation and execution.
    """

    @staticmethod
    def _step_id(asset_id: str) -> str:
        return f"construct:{asset_id}"

    def generate(
        self,
        architecture: ArchitectureCompositionResult,
    ) -> ConstructionPlanResult:
        if not isinstance(
            architecture,
            ArchitectureCompositionResult,
        ):
            raise TypeError(
                "architecture must be "
                "ArchitectureCompositionResult"
            )

        if not architecture.composed:
            return ConstructionPlanResult(
                requirement_name=architecture.requirement_name,
                steps=(),
                execution_order=(),
                blocked_steps=tuple(
                    architecture.unresolved_dependencies
                ),
                generated=False,
                executable=False,
                score=0.0,
                reasons=(
                    "architecture_not_composed",
                    "construction_plan_blocked",
                ),
                metadata={
                    "architecture_unit_count": len(
                        architecture.units
                    ),
                    "step_count": 0,
                    "blocked_count": len(
                        architecture.unresolved_dependencies
                    ),
                },
            )

        steps: list[ConstructionStep] = []
        execution_order: list[str] = []

        for unit in sorted(
            architecture.units,
            key=lambda value: (
                value.order,
                value.asset_id,
            ),
        ):
            step_id = self._step_id(
                unit.asset_id
            )

            dependencies = tuple(
                self._step_id(
                    dependency
                )
                for dependency in unit.dependencies
                if dependency
                in architecture.dependency_order
            )

            steps.append(
                ConstructionStep(
                    step_id=step_id,
                    order=unit.order,
                    asset_id=unit.asset_id,
                    action="construct_asset",
                    dependencies=dependencies,
                    metadata={
                        "architecture_order": unit.order,
                    },
                )
            )

            execution_order.append(step_id)

        executable = (
            bool(steps)
            and not architecture.unresolved_dependencies
            and not architecture.cycles
            and len(steps)
            == len(architecture.units)
        )

        reasons = [
            "architecture_received",
            "construction_steps_generated",
        ]

        if executable:
            reasons.append(
                "construction_plan_executable"
            )
        else:
            reasons.append(
                "construction_plan_blocked"
            )

        score = (
            10.0
            if executable
            else 0.0
        )

        return ConstructionPlanResult(
            requirement_name=architecture.requirement_name,
            steps=tuple(steps),
            execution_order=tuple(
                execution_order
            ),
            blocked_steps=(),
            generated=True,
            executable=executable,
            score=score,
            reasons=tuple(reasons),
            metadata={
                "architecture_unit_count": len(
                    architecture.units
                ),
                "step_count": len(steps),
                "blocked_count": 0,
            },
        )

    def generate_from_architecture(
        self,
        architecture: ArchitectureCompositionResult,
    ) -> ConstructionPlanResult:
        return self.generate(
            architecture
        )


__all__ = [
    "ConstructionStep",
    "ConstructionPlanResult",
    "CodeLibraryConstructionPlanner",
]
