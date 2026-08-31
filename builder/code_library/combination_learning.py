from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CombinationObservation:
    asset_ids: tuple[str, ...]
    successful: bool
    score: float
    context_key: str = ""
    project_id: str = ""
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized = tuple(
            dict.fromkeys(
                asset_id.strip()
                for asset_id in self.asset_ids
                if asset_id and asset_id.strip()
            )
        )

        if not normalized:
            raise ValueError(
                "asset_ids must contain at least one asset"
            )

        if not 0.0 <= float(self.score) <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

        object.__setattr__(
            self,
            "asset_ids",
            tuple(sorted(normalized)),
        )

    @property
    def combination_key(self) -> tuple[str, ...]:
        return self.asset_ids

    def to_dict(self) -> dict:
        return {
            "asset_ids": list(self.asset_ids),
            "successful": self.successful,
            "score": self.score,
            "context_key": self.context_key,
            "project_id": self.project_id,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class CombinationLearningContext:
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
                        value.strip().lower()
                        for value in self.capabilities
                        if value.strip()
                    )
                ),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.dependencies
                        if value.strip()
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
class CombinationLearningResult:
    asset_ids: tuple[str, ...]
    observation_count: int
    success_count: int
    failure_count: int
    success_rate: float
    average_score: float
    confidence: float
    successful: bool
    context_key: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "asset_ids": list(self.asset_ids),
            "observation_count": self.observation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "confidence": self.confidence,
            "successful": self.successful,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
        }


@dataclass
class _CombinationBucket:
    observations: list[CombinationObservation] = field(
        default_factory=list
    )


class CodeLibraryCombinationLearningEngine:
    """
    Learns empirically successful asset combinations.

    Combination evidence is stored independently from CodeAsset metadata.
    This permits successful-stack detection to improve over time without
    mutating the canonical asset definitions.
    """

    def __init__(self) -> None:
        self._buckets: dict[
            tuple[tuple[str, ...], str],
            _CombinationBucket,
        ] = {}

    @staticmethod
    def normalize_asset_ids(
        asset_ids: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = tuple(
            dict.fromkeys(
                asset_id.strip()
                for asset_id in asset_ids
                if asset_id and asset_id.strip()
            )
        )

        if not normalized:
            raise ValueError(
                "asset_ids must contain at least one asset"
            )

        return tuple(sorted(normalized))

    def observe(
        self,
        observation: CombinationObservation,
    ) -> CombinationLearningResult:
        key = (
            observation.combination_key,
            observation.context_key,
        )

        bucket = self._buckets.setdefault(
            key,
            _CombinationBucket(),
        )

        bucket.observations.append(observation)

        return self._result(
            observation.combination_key,
            observation.context_key,
        )

    def observe_result(
        self,
        asset_ids: Iterable[str],
        *,
        successful: bool,
        score: float,
        context: CombinationLearningContext | None = None,
        reasons: Iterable[str] = (),
    ) -> CombinationLearningResult:
        context = context or CombinationLearningContext()

        observation = CombinationObservation(
            asset_ids=self.normalize_asset_ids(asset_ids),
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
        asset_ids: Iterable[str],
        *,
        context: CombinationLearningContext | None = None,
    ) -> CombinationLearningResult:
        context = context or CombinationLearningContext()

        normalized = self.normalize_asset_ids(asset_ids)

        return self._result(
            normalized,
            context.key(),
        )

    def is_successful(
        self,
        asset_ids: Iterable[str],
        *,
        context: CombinationLearningContext | None = None,
    ) -> bool:
        return self.learn(
            asset_ids,
            context=context,
        ).successful

    def observations(
        self,
        asset_ids: Iterable[str],
        *,
        context: CombinationLearningContext | None = None,
    ) -> tuple[CombinationObservation, ...]:
        context = context or CombinationLearningContext()

        normalized = self.normalize_asset_ids(asset_ids)

        bucket = self._buckets.get(
            (
                normalized,
                context.key(),
            )
        )

        if bucket is None:
            return ()

        return tuple(bucket.observations)

    def successful_combinations(
        self,
        *,
        context: CombinationLearningContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> tuple[CombinationLearningResult, ...]:
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
            combination,
            bucket_context,
        ) in self._buckets:
            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                combination,
                bucket_context,
            )

            if (
                result.observation_count
                >= minimum_observations
                and result.success_rate
                >= minimum_success_rate
                and result.successful
            ):
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    -result.confidence,
                    result.asset_ids,
                    result.context_key,
                ),
            )
        )

    def combination_keys(self) -> tuple[tuple[str, ...], ...]:
        return tuple(
            sorted(
                {
                    combination
                    for combination, _ in self._buckets
                }
            )
        )

    def context_keys(
        self,
        asset_ids: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = self.normalize_asset_ids(asset_ids)

        return tuple(
            sorted(
                context_key
                for combination, context_key
                in self._buckets
                if combination == normalized
            )
        )

    def clear(
        self,
        asset_ids: Iterable[str] | None = None,
        *,
        context: CombinationLearningContext | None = None,
    ) -> None:
        if asset_ids is None:
            self._buckets.clear()
            return

        context = context or CombinationLearningContext()

        normalized = self.normalize_asset_ids(asset_ids)

        self._buckets.pop(
            (
                normalized,
                context.key(),
            ),
            None,
        )

    def to_dict(self) -> dict:
        observations = []

        for combination, context_key in sorted(
            self._buckets
        ):
            bucket = self._buckets[
                (
                    combination,
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
                self.combination_keys()
            ),
            "observation_count": len(observations),
        }

    def _result(
        self,
        asset_ids: tuple[str, ...],
        context_key: str,
    ) -> CombinationLearningResult:
        bucket = self._buckets.get(
            (
                asset_ids,
                context_key,
            )
        )

        if bucket is None or not bucket.observations:
            return CombinationLearningResult(
                asset_ids=asset_ids,
                observation_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                average_score=0.0,
                confidence=0.0,
                successful=False,
                context_key=context_key,
                reasons=(
                    "no_combination_observations",
                ),
            )

        observations = tuple(bucket.observations)

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

        successful = (
            success_rate >= 0.6
            and average_score >= 6.0
        )

        reasons: list[str] = []

        if successful:
            reasons.append(
                "successful_combination_detected"
            )
        else:
            reasons.append(
                "combination_not_successful"
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

        return CombinationLearningResult(
            asset_ids=asset_ids,
            observation_count=len(observations),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            average_score=average_score,
            confidence=confidence,
            successful=successful,
            context_key=context_key,
            reasons=tuple(reasons),
        )
