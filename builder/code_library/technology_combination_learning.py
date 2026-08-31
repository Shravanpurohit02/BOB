from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class TechnologyCombinationContext:
    language: str = ""
    framework: str = ""
    runtime: str = ""
    technologies: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    project_id: str = ""

    def key(self) -> str:
        return "|".join(
            (
                self.language.strip().lower(),
                self.framework.strip().lower(),
                self.runtime.strip().lower(),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.technologies
                        if value and value.strip()
                    )
                ),
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
            )
        )

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "technologies": list(self.technologies),
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "project_id": self.project_id,
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class TechnologyCombinationObservation:
    technologies: tuple[str, ...]
    successful: bool
    score: float
    context_key: str = ""
    project_id: str = ""
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized = tuple(
            sorted(
                dict.fromkeys(
                    technology.strip().lower()
                    for technology in self.technologies
                    if technology and technology.strip()
                )
            )
        )

        if not normalized:
            raise ValueError(
                "technologies must contain at least one technology"
            )

        if not 0.0 <= float(self.score) <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

        object.__setattr__(
            self,
            "technologies",
            normalized,
        )

    def to_dict(self) -> dict:
        return {
            "technologies": list(self.technologies),
            "successful": self.successful,
            "score": self.score,
            "context_key": self.context_key,
            "project_id": self.project_id,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class TechnologyCombinationResult:
    technologies: tuple[str, ...]
    observation_count: int
    success_count: int
    failure_count: int
    success_rate: float
    average_score: float
    confidence: float
    proven: bool
    context_key: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "technologies": list(self.technologies),
            "observation_count": self.observation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "confidence": self.confidence,
            "proven": self.proven,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
        }


@dataclass
class _TechnologyBucket:
    observations: list[
        TechnologyCombinationObservation
    ] = field(default_factory=list)


class CodeLibraryTechnologyCombinationLearningEngine:
    """
    Learns historically successful technology combinations.

    Technology combinations are normalized independently from asset
    identity so that the learned signal can be reused when evaluating
    different code-library assets that use the same technology stack.
    """

    def __init__(self) -> None:
        self._buckets: dict[
            tuple[tuple[str, ...], str],
            _TechnologyBucket,
        ] = {}

    @staticmethod
    def normalize_technologies(
        technologies: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = tuple(
            sorted(
                dict.fromkeys(
                    technology.strip().lower()
                    for technology in technologies
                    if technology and technology.strip()
                )
            )
        )

        if not normalized:
            raise ValueError(
                "technologies must contain at least one technology"
            )

        return normalized

    def observe(
        self,
        observation: TechnologyCombinationObservation,
    ) -> TechnologyCombinationResult:
        key = (
            observation.technologies,
            observation.context_key,
        )

        bucket = self._buckets.setdefault(
            key,
            _TechnologyBucket(),
        )

        bucket.observations.append(observation)

        return self._result(
            observation.technologies,
            observation.context_key,
        )

    def observe_result(
        self,
        technologies: Iterable[str],
        *,
        successful: bool,
        score: float,
        context: TechnologyCombinationContext | None = None,
        reasons: Iterable[str] = (),
    ) -> TechnologyCombinationResult:
        context = (
            context
            or TechnologyCombinationContext()
        )

        normalized = self.normalize_technologies(
            technologies
        )

        observation = TechnologyCombinationObservation(
            technologies=normalized,
            successful=successful,
            score=float(score),
            context_key=context.key(),
            project_id=context.project_id,
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
        technologies: Iterable[str],
        *,
        context: TechnologyCombinationContext | None = None,
    ) -> TechnologyCombinationResult:
        context = (
            context
            or TechnologyCombinationContext()
        )

        normalized = self.normalize_technologies(
            technologies
        )

        return self._result(
            normalized,
            context.key(),
        )

    def proven(
        self,
        technologies: Iterable[str],
        *,
        context: TechnologyCombinationContext | None = None,
    ) -> bool:
        return self.learn(
            technologies,
            context=context,
        ).proven

    def technology_combinations(
        self,
    ) -> tuple[tuple[str, ...], ...]:
        return tuple(
            sorted(
                {
                    technologies
                    for technologies, _ in self._buckets
                }
            )
        )

    def context_keys(
        self,
        technologies: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = self.normalize_technologies(
            technologies
        )

        return tuple(
            sorted(
                context_key
                for technology_key, context_key
                in self._buckets
                if technology_key == normalized
            )
        )

    def observations(
        self,
        technologies: Iterable[str],
        *,
        context: TechnologyCombinationContext | None = None,
    ) -> tuple[
        TechnologyCombinationObservation, ...
    ]:
        context = (
            context
            or TechnologyCombinationContext()
        )

        normalized = self.normalize_technologies(
            technologies
        )

        bucket = self._buckets.get(
            (
                normalized,
                context.key(),
            )
        )

        if bucket is None:
            return ()

        return tuple(bucket.observations)

    def proven_combinations(
        self,
        *,
        context: TechnologyCombinationContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> tuple[TechnologyCombinationResult, ...]:
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

        for technology_key, bucket_context in self._buckets:
            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                technology_key,
                bucket_context,
            )

            if (
                result.observation_count
                >= minimum_observations
                and result.success_rate
                >= minimum_success_rate
                and result.proven
            ):
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    -result.confidence,
                    result.technologies,
                ),
            )
        )

    def technologies_containing(
        self,
        technology: str,
        *,
        context: TechnologyCombinationContext | None = None,
    ) -> tuple[TechnologyCombinationResult, ...]:
        normalized_technology = (
            technology.strip().lower()
        )

        if not normalized_technology:
            raise ValueError(
                "technology must not be empty"
            )

        context_key = (
            None
            if context is None
            else context.key()
        )

        results = []

        for technology_key, bucket_context in self._buckets:
            if normalized_technology not in technology_key:
                continue

            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                technology_key,
                bucket_context,
            )

            if result.proven:
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    result.technologies,
                ),
            )
        )

    def clear(
        self,
        technologies: Iterable[str] | None = None,
        *,
        context: TechnologyCombinationContext | None = None,
    ) -> None:
        if technologies is None:
            self._buckets.clear()
            return

        context = (
            context
            or TechnologyCombinationContext()
        )

        normalized = self.normalize_technologies(
            technologies
        )

        self._buckets.pop(
            (
                normalized,
                context.key(),
            ),
            None,
        )

    def to_dict(self) -> dict:
        observations = []

        for technology_key, context_key in sorted(
            self._buckets
        ):
            bucket = self._buckets[
                (
                    technology_key,
                    context_key,
                )
            ]

            observations.extend(
                observation.to_dict()
                for observation in bucket.observations
            )

        return {
            "observations": observations,
            "combination_count": len(
                self.technology_combinations()
            ),
            "observation_count": len(observations),
        }

    def _result(
        self,
        technologies: tuple[str, ...],
        context_key: str,
    ) -> TechnologyCombinationResult:
        bucket = self._buckets.get(
            (
                technologies,
                context_key,
            )
        )

        if bucket is None or not bucket.observations:
            return TechnologyCombinationResult(
                technologies=technologies,
                observation_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                average_score=0.0,
                confidence=0.0,
                proven=False,
                context_key=context_key,
                reasons=("no_technology_observations",),
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

        proven = (
            success_rate >= 0.6
            and average_score >= 6.0
        )

        reasons: list[str] = []

        if proven:
            reasons.append(
                "technology_combination_proven"
            )
        else:
            reasons.append(
                "technology_combination_unproven"
            )

        if success_rate >= 0.8:
            reasons.append(
                "strong_success_history"
            )
        elif success_rate >= 0.6:
            reasons.append(
                "positive_success_history"
            )
        elif success_rate == 0.0:
            reasons.append(
                "no_success_history"
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

        return TechnologyCombinationResult(
            technologies=technologies,
            observation_count=len(observations),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            average_score=average_score,
            confidence=confidence,
            proven=proven,
            context_key=context_key,
            reasons=tuple(reasons),
        )
