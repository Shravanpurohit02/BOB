from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class ProjectAdaptationContext:
    project_id: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    technologies: tuple[str, ...] = ()

    def key(self) -> str:
        return "|".join(
            (
                self.project_id.strip(),
                self.language.strip().lower(),
                self.framework.strip().lower(),
                self.runtime.strip().lower(),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.capabilities
                        if value and value.strip()
                    )
                ),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.dependencies
                        if value and value.strip()
                    )
                ),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.technologies
                        if value and value.strip()
                    )
                ),
            )
        )

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "technologies": list(self.technologies),
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class ProjectAdaptationObservation:
    source_asset_ids: tuple[str, ...]
    adapted_asset_ids: tuple[str, ...]
    successful: bool
    score: float
    context_key: str
    project_id: str = ""
    adaptation_type: str = "project_adaptation"
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        source = tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in self.source_asset_ids
                    if value and value.strip()
                )
            )
        )

        adapted = tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in self.adapted_asset_ids
                    if value and value.strip()
                )
            )
        )

        if not source:
            raise ValueError(
                "source_asset_ids must contain at least one asset"
            )

        if not adapted:
            raise ValueError(
                "adapted_asset_ids must contain at least one asset"
            )

        if not self.context_key:
            raise ValueError(
                "context_key must not be empty"
            )

        if not 0.0 <= float(self.score) <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

        if not self.adaptation_type.strip():
            raise ValueError(
                "adaptation_type must not be empty"
            )

        object.__setattr__(
            self,
            "source_asset_ids",
            source,
        )

        object.__setattr__(
            self,
            "adapted_asset_ids",
            adapted,
        )

    def to_dict(self) -> dict:
        return {
            "source_asset_ids": list(self.source_asset_ids),
            "adapted_asset_ids": list(self.adapted_asset_ids),
            "successful": self.successful,
            "score": self.score,
            "context_key": self.context_key,
            "project_id": self.project_id,
            "adaptation_type": self.adaptation_type,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class ProjectAdaptationResult:
    source_asset_ids: tuple[str, ...]
    adapted_asset_ids: tuple[str, ...]
    observation_count: int
    success_count: int
    failure_count: int
    success_rate: float
    average_score: float
    confidence: float
    reusable: bool
    context_key: str
    project_id: str
    adaptation_type: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "source_asset_ids": list(self.source_asset_ids),
            "adapted_asset_ids": list(self.adapted_asset_ids),
            "observation_count": self.observation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "confidence": self.confidence,
            "reusable": self.reusable,
            "context_key": self.context_key,
            "project_id": self.project_id,
            "adaptation_type": self.adaptation_type,
            "reasons": list(self.reasons),
        }


@dataclass
class _AdaptationBucket:
    observations: list[
        ProjectAdaptationObservation
    ] = field(default_factory=list)


class CodeLibraryProjectAdaptationLearningEngine:
    """
    Learns successful project-specific adaptations.

    An adaptation maps a reusable source asset set to an adapted asset
    set for a particular project/context. Historical success is used
    to determine whether the adaptation is suitable for reuse in the
    same or a compatible project context.
    """

    def __init__(self) -> None:
        self._buckets: dict[
            tuple[
                tuple[str, ...],
                tuple[str, ...],
                str,
                str,
            ],
            _AdaptationBucket,
        ] = {}

    @staticmethod
    def normalize_asset_ids(
        asset_ids: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in asset_ids
                    if value and value.strip()
                )
            )
        )

        if not normalized:
            raise ValueError(
                "asset_ids must contain at least one asset"
            )

        return normalized

    def observe(
        self,
        observation: ProjectAdaptationObservation,
    ) -> ProjectAdaptationResult:
        key = (
            observation.source_asset_ids,
            observation.adapted_asset_ids,
            observation.context_key,
            observation.adaptation_type,
        )

        bucket = self._buckets.setdefault(
            key,
            _AdaptationBucket(),
        )

        bucket.observations.append(observation)

        return self._result(
            observation.source_asset_ids,
            observation.adapted_asset_ids,
            observation.context_key,
            observation.adaptation_type,
        )

    def observe_result(
        self,
        source_asset_ids: Iterable[str],
        adapted_asset_ids: Iterable[str],
        *,
        successful: bool,
        score: float,
        context: ProjectAdaptationContext,
        adaptation_type: str = "project_adaptation",
        reasons: Iterable[str] = (),
    ) -> ProjectAdaptationResult:
        if not isinstance(
            context,
            ProjectAdaptationContext,
        ):
            raise TypeError(
                "context must be ProjectAdaptationContext"
            )

        source = self.normalize_asset_ids(
            source_asset_ids
        )

        adapted = self.normalize_asset_ids(
            adapted_asset_ids
        )

        observation = ProjectAdaptationObservation(
            source_asset_ids=source,
            adapted_asset_ids=adapted,
            successful=successful,
            score=float(score),
            context_key=context.key(),
            project_id=context.project_id,
            adaptation_type=adaptation_type,
            reasons=tuple(
                dict.fromkeys(
                    str(reason)
                    for reason in reasons
                    if str(reason)
                )
            ),
        )

        return self.observe(observation)

    def learn(
        self,
        source_asset_ids: Iterable[str],
        adapted_asset_ids: Iterable[str],
        *,
        context: ProjectAdaptationContext,
        adaptation_type: str = "project_adaptation",
    ) -> ProjectAdaptationResult:
        if not isinstance(
            context,
            ProjectAdaptationContext,
        ):
            raise TypeError(
                "context must be ProjectAdaptationContext"
            )

        source = self.normalize_asset_ids(
            source_asset_ids
        )

        adapted = self.normalize_asset_ids(
            adapted_asset_ids
        )

        return self._result(
            source,
            adapted,
            context.key(),
            adaptation_type,
        )

    def is_reusable(
        self,
        source_asset_ids: Iterable[str],
        adapted_asset_ids: Iterable[str],
        *,
        context: ProjectAdaptationContext,
        adaptation_type: str = "project_adaptation",
    ) -> bool:
        return self.learn(
            source_asset_ids,
            adapted_asset_ids,
            context=context,
            adaptation_type=adaptation_type,
        ).reusable

    def reusable_adaptations(
        self,
        *,
        context: ProjectAdaptationContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> tuple[ProjectAdaptationResult, ...]:
        if minimum_observations < 1:
            raise ValueError(
                "minimum_observations must be at least 1"
            )

        if not 0.0 <= minimum_success_rate <= 1.0:
            raise ValueError(
                "minimum_success_rate must be between 0.0 and 1.0"
            )

        context_key = (
            None
            if context is None
            else context.key()
        )

        results = []

        for (
            source,
            adapted,
            bucket_context,
            adaptation_type,
        ) in self._buckets:
            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                source,
                adapted,
                bucket_context,
                adaptation_type,
            )

            if (
                result.observation_count
                >= minimum_observations
                and result.success_rate
                >= minimum_success_rate
                and result.reusable
            ):
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    -result.confidence,
                    result.source_asset_ids,
                    result.adapted_asset_ids,
                ),
            )
        )

    def adaptations_for_source(
        self,
        source_asset_ids: Iterable[str],
        *,
        context: ProjectAdaptationContext | None = None,
    ) -> tuple[ProjectAdaptationResult, ...]:
        source = self.normalize_asset_ids(
            source_asset_ids
        )

        context_key = (
            None
            if context is None
            else context.key()
        )

        results = []

        for (
            bucket_source,
            bucket_adapted,
            bucket_context,
            adaptation_type,
        ) in self._buckets:
            if bucket_source != source:
                continue

            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                bucket_source,
                bucket_adapted,
                bucket_context,
                adaptation_type,
            )

            if result.reusable:
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    result.adapted_asset_ids,
                ),
            )
        )

    def project_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    observation.project_id
                    for bucket in self._buckets.values()
                    for observation in bucket.observations
                    if observation.project_id
                }
            )
        )

    def adaptation_types(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    adaptation_type
                    for (
                        _source,
                        _adapted,
                        _context,
                        adaptation_type,
                    ) in self._buckets
                }
            )
        )

    def clear(
        self,
        source_asset_ids: Iterable[str] | None = None,
        adapted_asset_ids: Iterable[str] | None = None,
        *,
        context: ProjectAdaptationContext | None = None,
        adaptation_type: str = "project_adaptation",
    ) -> None:
        if (
            source_asset_ids is None
            and adapted_asset_ids is None
        ):
            self._buckets.clear()
            return

        if source_asset_ids is None:
            raise ValueError(
                "source_asset_ids is required when adapted_asset_ids is provided"
            )

        if adapted_asset_ids is None:
            raise ValueError(
                "adapted_asset_ids is required when source_asset_ids is provided"
            )

        if context is None:
            raise ValueError(
                "context is required when clearing a specific adaptation"
            )

        source = self.normalize_asset_ids(
            source_asset_ids
        )

        adapted = self.normalize_asset_ids(
            adapted_asset_ids
        )

        self._buckets.pop(
            (
                source,
                adapted,
                context.key(),
                adaptation_type,
            ),
            None,
        )

    def observations(
        self,
        source_asset_ids: Iterable[str],
        adapted_asset_ids: Iterable[str],
        *,
        context: ProjectAdaptationContext,
        adaptation_type: str = "project_adaptation",
    ) -> tuple[
        ProjectAdaptationObservation, ...
    ]:
        result = self.learn(
            source_asset_ids,
            adapted_asset_ids,
            context=context,
            adaptation_type=adaptation_type,
        )

        bucket = self._buckets.get(
            (
                result.source_asset_ids,
                result.adapted_asset_ids,
                result.context_key,
                result.adaptation_type,
            )
        )

        if bucket is None:
            return ()

        return tuple(bucket.observations)

    def to_dict(self) -> dict:
        observations = []

        for key in sorted(self._buckets):
            bucket = self._buckets[key]

            observations.extend(
                observation.to_dict()
                for observation in bucket.observations
            )

        return {
            "observations": observations,
            "adaptation_count": len(self._buckets),
            "observation_count": len(observations),
            "project_count": len(self.project_ids()),
        }

    def _result(
        self,
        source_asset_ids: tuple[str, ...],
        adapted_asset_ids: tuple[str, ...],
        context_key: str,
        adaptation_type: str,
    ) -> ProjectAdaptationResult:
        bucket = self._buckets.get(
            (
                source_asset_ids,
                adapted_asset_ids,
                context_key,
                adaptation_type,
            )
        )

        if bucket is None or not bucket.observations:
            return ProjectAdaptationResult(
                source_asset_ids=source_asset_ids,
                adapted_asset_ids=adapted_asset_ids,
                observation_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                average_score=0.0,
                confidence=0.0,
                reusable=False,
                context_key=context_key,
                project_id="",
                adaptation_type=adaptation_type,
                reasons=("no_adaptation_observations",),
            )

        observations = tuple(
            bucket.observations
        )

        success_count = sum(
            1
            for observation in observations
            if observation.successful
        )

        failure_count = (
            len(observations) - success_count
        )

        success_rate = (
            success_count / len(observations)
        )

        average_score = (
            sum(
                observation.score
                for observation in observations
            )
            / len(observations)
        )

        confidence = min(
            1.0,
            len(observations) / 5.0,
        )

        reusable = (
            success_rate >= 0.6
            and average_score >= 6.0
        )

        project_id = observations[-1].project_id

        reasons: list[str] = []

        if reusable:
            reasons.append(
                "project_adaptation_reusable"
            )
        else:
            reasons.append(
                "project_adaptation_not_reusable"
            )

        if success_rate >= 0.8:
            reasons.append(
                "strong_adaptation_history"
            )
        elif success_rate >= 0.6:
            reasons.append(
                "positive_adaptation_history"
            )
        elif success_rate == 0.0:
            reasons.append(
                "no_successful_adaptations"
            )

        if confidence >= 0.8:
            reasons.append(
                "high_observation_confidence"
            )
        elif confidence >= 0.4:
            reasons.append(
                "moderate_observation_confidence"
            )
        else:
            reasons.append(
                "low_observation_confidence"
            )

        return ProjectAdaptationResult(
            source_asset_ids=source_asset_ids,
            adapted_asset_ids=adapted_asset_ids,
            observation_count=len(observations),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            average_score=average_score,
            confidence=confidence,
            reusable=reusable,
            context_key=context_key,
            project_id=project_id,
            adaptation_type=adaptation_type,
            reasons=tuple(reasons),
        )
