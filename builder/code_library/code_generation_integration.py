from __future__ import annotations

from dataclasses import dataclass

from .construction_plan import (
    ConstructionPlanResult,
    ConstructionStep,
)
from .repository_intelligence import (
    RepositoryIntelligenceResult,
)


@dataclass(frozen=True)
class GenerationRequest:
    step_id: str
    asset_id: str
    action: str
    repository_root: str
    existing_files: tuple[str, ...] = ()
    integration_points: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.step_id.strip():
            raise ValueError("step_id must not be empty")

        if not self.asset_id.strip():
            raise ValueError("asset_id must not be empty")

        if not self.action.strip():
            raise ValueError("action must not be empty")

        if not self.repository_root.strip():
            raise ValueError(
                "repository_root must not be empty"
            )

        object.__setattr__(
            self,
            "existing_files",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.existing_files
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "integration_points",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.integration_points
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

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
            "asset_id": self.asset_id,
            "action": self.action,
            "repository_root": self.repository_root,
            "existing_files": list(
                self.existing_files
            ),
            "integration_points": list(
                self.integration_points
            ),
            "dependencies": list(
                self.dependencies
            ),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class GenerationIntegrationResult:
    requirement_name: str
    requests: tuple[GenerationRequest, ...]
    generated: bool
    executable: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "requests": [
                request.to_dict()
                for request in self.requests
            ],
            "generated": self.generated,
            "executable": self.executable,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryCodeGenerationIntegration:
    """
    Converts the validated CL-15.5 construction plan and CL-15.6
    repository intelligence into deterministic generation requests.

    This layer prepares generation work; it does not execute generated
    code or invent an external LLM provider.
    """

    def build_request(
        self,
        step: ConstructionStep,
        repository: RepositoryIntelligenceResult,
    ) -> GenerationRequest:
        if not isinstance(
            step,
            ConstructionStep,
        ):
            raise TypeError(
                "step must be ConstructionStep"
            )

        if not isinstance(
            repository,
            RepositoryIntelligenceResult,
        ):
            raise TypeError(
                "repository must be "
                "RepositoryIntelligenceResult"
            )

        return GenerationRequest(
            step_id=step.step_id,
            asset_id=step.asset_id,
            action=step.action,
            repository_root=repository.repository_root,
            existing_files=tuple(
                file.path
                for file in repository.files
                if not file.is_directory
            ),
            integration_points=(
                repository.integration_points
            ),
            dependencies=step.dependencies,
            metadata={
                "repository_compatible":
                    repository.compatible,
                "repository_score":
                    repository.score,
            },
        )

    def prepare(
        self,
        plan: ConstructionPlanResult,
        repository: RepositoryIntelligenceResult,
    ) -> GenerationIntegrationResult:
        if not isinstance(
            plan,
            ConstructionPlanResult,
        ):
            raise TypeError(
                "plan must be ConstructionPlanResult"
            )

        if not isinstance(
            repository,
            RepositoryIntelligenceResult,
        ):
            raise TypeError(
                "repository must be "
                "RepositoryIntelligenceResult"
            )

        if not plan.executable:
            return GenerationIntegrationResult(
                requirement_name=plan.requirement_name,
                requests=(),
                generated=False,
                executable=False,
                score=0.0,
                reasons=(
                    "construction_plan_not_executable",
                    "generation_preparation_blocked",
                ),
                metadata={
                    "step_count": len(plan.steps),
                    "request_count": 0,
                },
            )

        if not repository.analyzed:
            return GenerationIntegrationResult(
                requirement_name=plan.requirement_name,
                requests=(),
                generated=False,
                executable=False,
                score=0.0,
                reasons=(
                    "repository_not_analyzed",
                    "generation_preparation_blocked",
                ),
                metadata={
                    "step_count": len(plan.steps),
                    "request_count": 0,
                },
            )

        requests = tuple(
            self.build_request(
                step,
                repository,
            )
            for step in sorted(
                plan.steps,
                key=lambda value: (
                    value.order,
                    value.step_id,
                ),
            )
        )

        executable = (
            bool(requests)
            and repository.compatible
            and len(requests)
            == len(plan.steps)
        )

        reasons = [
            "construction_plan_received",
            "repository_intelligence_received",
            "generation_requests_prepared",
        ]

        if executable:
            reasons.append(
                "generation_requests_executable"
            )
        else:
            reasons.append(
                "generation_requests_blocked"
            )

        score = 10.0 if executable else 0.0

        return GenerationIntegrationResult(
            requirement_name=plan.requirement_name,
            requests=requests,
            generated=True,
            executable=executable,
            score=score,
            reasons=tuple(reasons),
            metadata={
                "step_count": len(plan.steps),
                "request_count": len(requests),
                "repository_file_count":
                    len(repository.files),
                "integration_point_count":
                    len(repository.integration_points),
            },
        )

    def prepare_generation(
        self,
        plan: ConstructionPlanResult,
        repository: RepositoryIntelligenceResult,
    ) -> GenerationIntegrationResult:
        return self.prepare(
            plan,
            repository,
        )


__all__ = [
    "GenerationRequest",
    "GenerationIntegrationResult",
    "CodeLibraryCodeGenerationIntegration",
]
