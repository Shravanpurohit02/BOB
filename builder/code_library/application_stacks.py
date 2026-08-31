from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class ApplicationStackObservation:
    stack_id: str
    asset_ids: tuple[str, ...]
    successful: bool
    score: float
    context_key: str = ""
    project_id: str = ""
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.stack_id.strip():
            raise ValueError("stack_id must not be empty")

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

    def to_dict(self) -> dict:
        return {
            "stack_id": self.stack_id,
            "asset_ids": list(self.asset_ids),
            "successful": self.successful,
            "score": self.score,
            "context_key": self.context_key,
            "project_id": self.project_id,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class ApplicationStackContext:
    language: str = ""
    framework: str = ""
    runtime: str = ""
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
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "project_id": self.project_id,
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class ApplicationStackResult:
    stack_id: str
    asset_ids: tuple[str, ...]
    observation_count: int
    success_count: int
    failure_count: int
    success_rate: float
    average_score: float
    confidence: float
    reusable: bool
    context_key: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "stack_id": self.stack_id,
            "asset_ids": list(self.asset_ids),
            "observation_count": self.observation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "confidence": self.confidence,
            "reusable": self.reusable,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
        }


@dataclass
class _StackBucket:
    observations: list[ApplicationStackObservation] = field(
        default_factory=list
    )


class CodeLibraryApplicationStackEngine:
    """
    Learns reusable application stacks from successful project outcomes.

    A stack is a named, repeatable group of assets whose historical
    outcomes indicate that the group can be safely reused in a matching
    project context.
    """

    def __init__(self) -> None:
        self._buckets: dict[
            tuple[str, str],
            _StackBucket,
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
        observation: ApplicationStackObservation,
    ) -> ApplicationStackResult:
        key = (
            observation.stack_id,
            observation.context_key,
        )

        bucket = self._buckets.setdefault(
            key,
            _StackBucket(),
        )

        bucket.observations.append(observation)

        return self._result(
            observation.stack_id,
            observation.context_key,
        )

    def observe_result(
        self,
        stack_id: str,
        asset_ids: Iterable[str],
        *,
        successful: bool,
        score: float,
        context: ApplicationStackContext | None = None,
        reasons: Iterable[str] = (),
    ) -> ApplicationStackResult:
        context = context or ApplicationStackContext()

        observation = ApplicationStackObservation(
            stack_id=stack_id,
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
        stack_id: str,
        *,
        context: ApplicationStackContext | None = None,
    ) -> ApplicationStackResult:
        context = context or ApplicationStackContext()

        if not stack_id.strip():
            raise ValueError("stack_id must not be empty")

        return self._result(
            stack_id,
            context.key(),
        )

    def is_reusable(
        self,
        stack_id: str,
        *,
        context: ApplicationStackContext | None = None,
    ) -> bool:
        return self.learn(
            stack_id,
            context=context,
        ).reusable

    def stack_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    stack_id
                    for stack_id, _ in self._buckets
                }
            )
        )

    def context_keys(
        self,
        stack_id: str,
    ) -> tuple[str, ...]:
        if not stack_id.strip():
            raise ValueError("stack_id must not be empty")

        return tuple(
            sorted(
                context_key
                for observed_stack_id, context_key
                in self._buckets
                if observed_stack_id == stack_id
            )
        )

    def observations(
        self,
        stack_id: str,
        *,
        context: ApplicationStackContext | None = None,
    ) -> tuple[ApplicationStackObservation, ...]:
        context = context or ApplicationStackContext()

        if not stack_id.strip():
            raise ValueError("stack_id must not be empty")

        bucket = self._buckets.get(
            (
                stack_id,
                context.key(),
            )
        )

        if bucket is None:
            return ()

        return tuple(bucket.observations)

    def reusable_stacks(
        self,
        *,
        context: ApplicationStackContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> tuple[ApplicationStackResult, ...]:
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

        for stack_id, bucket_context in self._buckets:
            if (
                context_key is not None
                and bucket_context != context_key
            ):
                continue

            result = self._result(
                stack_id,
                bucket_context,
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
                    result.stack_id,
                    result.context_key,
                ),
            )
        )

    def stack_for_assets(
        self,
        asset_ids: Iterable[str],
        *,
        context: ApplicationStackContext | None = None,
    ) -> tuple[ApplicationStackResult, ...]:
        context = context or ApplicationStackContext()

        target = self.normalize_asset_ids(asset_ids)

        results = []

        for stack_id, bucket_context in self._buckets:
            if bucket_context != context.key():
                continue

            result = self._result(
                stack_id,
                bucket_context,
            )

            if (
                result.reusable
                and result.asset_ids == target
            ):
                results.append(result)

        return tuple(
            sorted(
                results,
                key=lambda result: (
                    -result.success_rate,
                    -result.average_score,
                    result.stack_id,
                ),
            )
        )

    def clear(
        self,
        stack_id: str | None = None,
        *,
        context: ApplicationStackContext | None = None,
    ) -> None:
        if stack_id is None:
            self._buckets.clear()
            return

        if not stack_id.strip():
            raise ValueError("stack_id must not be empty")

        context = context or ApplicationStackContext()

        self._buckets.pop(
            (
                stack_id,
                context.key(),
            ),
            None,
        )

    def to_dict(self) -> dict:
        observations = []

        for stack_id, context_key in sorted(
            self._buckets
        ):
            bucket = self._buckets[
                (
                    stack_id,
                    context_key,
                )
            ]

            observations.extend(
                observation.to_dict()
                for observation in bucket.observations
            )

        return {
            "observations": observations,
            "stack_count": len(self.stack_ids()),
            "observation_count": len(observations),
        }

    def _result(
        self,
        stack_id: str,
        context_key: str,
    ) -> ApplicationStackResult:
        bucket = self._buckets.get(
            (
                stack_id,
                context_key,
            )
        )

        if bucket is None or not bucket.observations:
            return ApplicationStackResult(
                stack_id=stack_id,
                asset_ids=(),
                observation_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                average_score=0.0,
                confidence=0.0,
                reusable=False,
                context_key=context_key,
                reasons=("no_stack_observations",),
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

        reusable = (
            success_rate >= 0.6
            and average_score >= 6.0
        )

        # Use the most recent observation as the canonical asset
        # membership for the learned stack. All observations for one
        # stack/context are expected to describe the same reusable stack.
        asset_ids = observations[-1].asset_ids

        reasons: list[str] = []

        if reusable:
            reasons.append(
                "reusable_stack_detected"
            )
        else:
            reasons.append(
                "stack_not_reusable"
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

        return ApplicationStackResult(
            stack_id=stack_id,
            asset_ids=asset_ids,
            observation_count=len(observations),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            average_score=average_score,
            confidence=confidence,
            reusable=reusable,
            context_key=context_key,
            reasons=tuple(reasons),
        )
