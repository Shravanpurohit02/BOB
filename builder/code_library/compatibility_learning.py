from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CompatibilityObservation:
    asset_id: str
    compatible: bool
    score: float
    context_key: str = ""
    reasons: tuple[str, ...] = ()
    project_id: str = ""

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id must not be empty")

        if not 0.0 <= float(self.score) <= 10.0:
            raise ValueError("score must be between 0.0 and 10.0")

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "compatible": self.compatible,
            "score": self.score,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
            "project_id": self.project_id,
        }


@dataclass(frozen=True)
class CompatibilityLearningContext:
    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    project_id: str = ""

    def key(self) -> str:
        return "|".join(
            (
                self.language.strip().lower(),
                self.framework.strip().lower(),
                self.runtime.strip().lower(),
                self.asset_type.strip().lower(),
                ",".join(
                    sorted(
                        item.strip().lower()
                        for item in self.capabilities
                        if item.strip()
                    )
                ),
                ",".join(
                    sorted(
                        item.strip().lower()
                        for item in self.dependencies
                        if item.strip()
                    )
                ),
            )
        )

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "asset_type": self.asset_type,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "project_id": self.project_id,
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class CompatibilityLearningResult:
    asset_id: str
    observation_count: int
    success_count: int
    failure_count: int
    success_rate: float
    average_score: float
    confidence: float
    compatible: bool
    context_key: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "observation_count": self.observation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "confidence": self.confidence,
            "compatible": self.compatible,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
        }


@dataclass
class _ObservationBucket:
    observations: list[CompatibilityObservation] = field(
        default_factory=list
    )


class CodeLibraryCompatibilityLearningEngine:
    """
    Learns empirical asset compatibility from observed composition and
    assembly outcomes.

    This layer deliberately does not mutate CodeAsset compatibility
    metadata. It records evidence separately so learned behavior can be
    inspected, serialized, replaced, or incorporated into later
    recommendation decisions without corrupting source asset metadata.
    """

    def __init__(self) -> None:
        self._buckets: dict[
            tuple[str, str],
            _ObservationBucket,
        ] = {}

    def observe(
        self,
        observation: CompatibilityObservation,
    ) -> CompatibilityLearningResult:
        key = (
            observation.asset_id,
            observation.context_key,
        )

        bucket = self._buckets.setdefault(
            key,
            _ObservationBucket(),
        )

        bucket.observations.append(observation)

        return self._result(
            observation.asset_id,
            observation.context_key,
        )

    def observe_result(
        self,
        asset_id: str,
        *,
        compatible: bool,
        score: float,
        context: CompatibilityLearningContext | None = None,
        reasons: Iterable[str] = (),
    ) -> CompatibilityLearningResult:
        context = context or CompatibilityLearningContext()

        observation = CompatibilityObservation(
            asset_id=asset_id,
            compatible=compatible,
            score=float(score),
            context_key=context.key(),
            reasons=tuple(
                dict.fromkeys(
                    str(reason)
                    for reason in reasons
                    if str(reason)
                )
            ),
            project_id=context.project_id,
        )

        return self.observe(observation)

    def learn(
        self,
        asset_id: str,
        *,
        context: CompatibilityLearningContext | None = None,
    ) -> CompatibilityLearningResult:
        context = context or CompatibilityLearningContext()

        return self._result(
            asset_id,
            context.key(),
        )

    def is_compatible(
        self,
        asset_id: str,
        *,
        context: CompatibilityLearningContext | None = None,
    ) -> bool:
        result = self.learn(
            asset_id,
            context=context,
        )
        return result.compatible

    def observations(
        self,
        asset_id: str,
        *,
        context: CompatibilityLearningContext | None = None,
    ) -> tuple[CompatibilityObservation, ...]:
        context = context or CompatibilityLearningContext()

        bucket = self._buckets.get(
            (
                asset_id,
                context.key(),
            )
        )

        if bucket is None:
            return ()

        return tuple(bucket.observations)

    def asset_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    asset_id
                    for asset_id, _ in self._buckets
                }
            )
        )

    def context_keys(
        self,
        asset_id: str,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                context_key
                for observed_asset_id, context_key
                in self._buckets
                if observed_asset_id == asset_id
            )
        )

    def clear(
        self,
        asset_id: str | None = None,
        *,
        context: CompatibilityLearningContext | None = None,
    ) -> None:
        if asset_id is None:
            self._buckets.clear()
            return

        context = context or CompatibilityLearningContext()

        self._buckets.pop(
            (
                asset_id,
                context.key(),
            ),
            None,
        )

    def to_dict(self) -> dict:
        observations = []

        for asset_id, context_key in sorted(
            self._buckets
        ):
            bucket = self._buckets[
                (asset_id, context_key)
            ]

            observations.extend(
                observation.to_dict()
                for observation in bucket.observations
            )

        return {
            "observations": observations,
            "asset_count": len(self.asset_ids()),
            "observation_count": len(observations),
        }

    def _result(
        self,
        asset_id: str,
        context_key: str,
    ) -> CompatibilityLearningResult:
        bucket = self._buckets.get(
            (
                asset_id,
                context_key,
            )
        )

        if bucket is None or not bucket.observations:
            return CompatibilityLearningResult(
                asset_id=asset_id,
                observation_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                average_score=0.0,
                confidence=0.0,
                compatible=False,
                context_key=context_key,
                reasons=("no_compatibility_observations",),
            )

        observations = tuple(bucket.observations)

        success_count = sum(
            1
            for observation in observations
            if observation.compatible
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

        # Confidence increases with repeated independent observations
        # and is capped at 1.0. A single observation is intentionally
        # informative but not treated as high-confidence evidence.
        confidence = min(
            1.0,
            len(observations) / 5.0,
        )

        compatible = (
            success_rate >= 0.6
            and average_score >= 6.0
        )

        reasons: list[str] = []

        if compatible:
            reasons.append(
                "learned_compatibility"
            )
        else:
            reasons.append(
                "learned_incompatibility"
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

        return CompatibilityLearningResult(
            asset_id=asset_id,
            observation_count=len(observations),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            average_score=average_score,
            confidence=confidence,
            compatible=compatible,
            context_key=context_key,
            reasons=tuple(reasons),
        )
