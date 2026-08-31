from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ConstructionRequirement:
    name: str
    description: str
    language: str = ""
    framework: str = ""
    runtime: str = ""
    platform: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.description.strip():
            raise ValueError(
                "description must not be empty"
            )

        for field_name in (
            "capabilities",
            "dependencies",
            "constraints",
            "tags",
        ):
            values = getattr(self, field_name)
            normalized = tuple(
                sorted(
                    dict.fromkeys(
                        value.strip().lower()
                        for value in values
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata or {}),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "platform": self.platform,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "constraints": list(self.constraints),
            "tags": list(self.tags),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class RequirementUnderstandingResult:
    requirement: ConstructionRequirement
    normalized: bool
    complete: bool
    score: float
    missing_fields: tuple[str, ...]
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement": self.requirement.to_dict(),
            "normalized": self.normalized,
            "complete": self.complete,
            "score": self.score,
            "missing_fields": list(
                self.missing_fields
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryRequirementUnderstanding:
    """
    Deterministically normalizes construction requirements into the
    canonical context consumed by CL-15 downstream stages.
    """

    REQUIRED_FIELDS = (
        "name",
        "description",
    )

    def understand(
        self,
        requirement: ConstructionRequirement,
    ) -> RequirementUnderstandingResult:
        if not isinstance(
            requirement,
            ConstructionRequirement,
        ):
            raise TypeError(
                "requirement must be ConstructionRequirement"
            )

        missing: list[str] = []

        for field_name in self.REQUIRED_FIELDS:
            value = getattr(
                requirement,
                field_name,
            )

            if not isinstance(value, str) or not value.strip():
                missing.append(field_name)

        reasons: list[str] = [
            "requirement_normalized"
        ]

        if requirement.capabilities:
            reasons.append(
                "capabilities_resolved"
            )

        if requirement.dependencies:
            reasons.append(
                "dependencies_resolved"
            )

        if requirement.constraints:
            reasons.append(
                "constraints_resolved"
            )

        if requirement.tags:
            reasons.append(
                "tags_resolved"
            )

        complete = not missing

        if complete:
            score = 10.0
            reasons.append(
                "requirement_complete"
            )
        else:
            score = max(
                0.0,
                10.0 - (
                    len(missing) * 5.0
                ),
            )
            reasons.append(
                "requirement_incomplete"
            )

        return RequirementUnderstandingResult(
            requirement=requirement,
            normalized=True,
            complete=complete,
            score=score,
            missing_fields=tuple(missing),
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "capability_count": len(
                    requirement.capabilities
                ),
                "dependency_count": len(
                    requirement.dependencies
                ),
                "constraint_count": len(
                    requirement.constraints
                ),
                "tag_count": len(
                    requirement.tags
                ),
            },
        )

    def from_values(
        self,
        *,
        name: str,
        description: str,
        language: str = "",
        framework: str = "",
        runtime: str = "",
        platform: str = "",
        capabilities: Iterable[str] = (),
        dependencies: Iterable[str] = (),
        constraints: Iterable[str] = (),
        tags: Iterable[str] = (),
        metadata: dict | None = None,
    ) -> RequirementUnderstandingResult:
        requirement = ConstructionRequirement(
            name=name,
            description=description,
            language=language.strip(),
            framework=framework.strip(),
            runtime=runtime.strip(),
            platform=platform.strip(),
            capabilities=tuple(capabilities),
            dependencies=tuple(dependencies),
            constraints=tuple(constraints),
            tags=tuple(tags),
            metadata=metadata,
        )

        return self.understand(requirement)

    def merge(
        self,
        base: ConstructionRequirement,
        override: ConstructionRequirement,
    ) -> ConstructionRequirement:
        if not isinstance(
            base,
            ConstructionRequirement,
        ):
            raise TypeError(
                "base must be ConstructionRequirement"
            )

        if not isinstance(
            override,
            ConstructionRequirement,
        ):
            raise TypeError(
                "override must be ConstructionRequirement"
            )

        return ConstructionRequirement(
            name=(
                override.name.strip()
                or base.name
            ),
            description=(
                override.description.strip()
                or base.description
            ),
            language=(
                override.language.strip()
                or base.language
            ),
            framework=(
                override.framework.strip()
                or base.framework
            ),
            runtime=(
                override.runtime.strip()
                or base.runtime
            ),
            platform=(
                override.platform.strip()
                or base.platform
            ),
            capabilities=(
                base.capabilities
                + override.capabilities
            ),
            dependencies=(
                base.dependencies
                + override.dependencies
            ),
            constraints=(
                base.constraints
                + override.constraints
            ),
            tags=(
                base.tags
                + override.tags
            ),
            metadata={
                **(base.metadata or {}),
                **(override.metadata or {}),
            },
        )


__all__ = [
    "ConstructionRequirement",
    "RequirementUnderstandingResult",
    "CodeLibraryRequirementUnderstanding",
]
