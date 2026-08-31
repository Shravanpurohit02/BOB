from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .execution_integration import (
    ExecutionIntegrationResult,
    ExecutionResult,
)


@dataclass(frozen=True)
class VerificationResult:
    step_id: str
    asset_id: str
    verified: bool
    success: bool
    output_valid: bool
    repository_valid: bool
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "asset_id": self.asset_id,
            "verified": self.verified,
            "success": self.success,
            "output_valid": self.output_valid,
            "repository_valid": self.repository_valid,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ExecutionVerificationResult:
    requirement_name: str
    results: tuple[VerificationResult, ...]
    verified: bool
    successful: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "results": [
                result.to_dict()
                for result in self.results
            ],
            "verified": self.verified,
            "successful": self.successful,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryExecutionResultVerifier:
    """
    Verifies execution results and the resulting repository state.

    Verification is deliberately deterministic and conservative:
    successful execution alone is insufficient unless the repository
    state can also be inspected successfully.
    """

    def verify_result(
        self,
        result: ExecutionResult,
        repository_root: str | Path,
    ) -> VerificationResult:
        if not isinstance(
            result,
            ExecutionResult,
        ):
            raise TypeError(
                "result must be ExecutionResult"
            )

        root = Path(repository_root)

        if not root.exists():
            raise FileNotFoundError(
                f"repository root does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"repository root is not a directory: {root}"
            )

        output_valid = (
            result.success
            and result.exit_code == 0
        )

        repository_valid = (
            root.exists()
            and root.is_dir()
        )

        verified = (
            result.executed
            and result.success
            and output_valid
            and repository_valid
        )

        reasons: list[str] = []

        if result.executed:
            reasons.append(
                "execution_performed"
            )
        else:
            reasons.append(
                "execution_not_performed"
            )

        if output_valid:
            reasons.append(
                "execution_output_valid"
            )
        else:
            reasons.append(
                "execution_output_invalid"
            )

        if repository_valid:
            reasons.append(
                "repository_state_valid"
            )
        else:
            reasons.append(
                "repository_state_invalid"
            )

        if verified:
            reasons.append(
                "execution_result_verified"
            )
        else:
            reasons.append(
                "execution_result_not_verified"
            )

        return VerificationResult(
            step_id=result.step_id,
            asset_id=result.asset_id,
            verified=verified,
            success=result.success,
            output_valid=output_valid,
            repository_valid=repository_valid,
            reasons=tuple(reasons),
            metadata={
                "repository_root": str(root),
                "exit_code": result.exit_code,
                "output_length": len(
                    result.output
                ),
                "error_length": len(
                    result.error
                ),
            },
        )

    def verify(
        self,
        execution: ExecutionIntegrationResult,
        repository_root: str | Path,
    ) -> ExecutionVerificationResult:
        if not isinstance(
            execution,
            ExecutionIntegrationResult,
        ):
            raise TypeError(
                "execution must be "
                "ExecutionIntegrationResult"
            )

        root = Path(repository_root)

        if not root.exists():
            raise FileNotFoundError(
                f"repository root does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"repository root is not a directory: {root}"
            )

        if not execution.results:
            return ExecutionVerificationResult(
                requirement_name=(
                    execution.requirement_name
                ),
                results=(),
                verified=False,
                successful=False,
                score=0.0,
                reasons=(
                    "no_execution_results",
                    "verification_blocked",
                ),
                metadata={
                    "result_count": 0,
                    "verified_count": 0,
                },
            )

        verified_results: list[VerificationResult] = []

        for result in execution.results:
            verified_results.append(
                self.verify_result(
                    result,
                    root,
                )
            )

        verified = (
            execution.successful
            and len(verified_results)
            == len(execution.results)
            and all(
                item.verified
                for item in verified_results
            )
        )

        verified_count = sum(
            1
            for item in verified_results
            if item.verified
        )

        reasons = [
            "execution_results_received",
            "repository_state_inspected",
            "execution_results_verified",
            (
                "verification_successful"
                if verified
                else "verification_failed"
            ),
        ]

        score = (
            10.0
            if verified
            else (
                10.0
                * (
                    verified_count
                    / max(
                        1,
                        len(verified_results),
                    )
                )
            )
        )

        return ExecutionVerificationResult(
            requirement_name=(
                execution.requirement_name
            ),
            results=tuple(verified_results),
            verified=verified,
            successful=verified,
            score=score,
            reasons=tuple(reasons),
            metadata={
                "result_count": len(
                    execution.results
                ),
                "verified_count": verified_count,
                "failed_count": (
                    len(verified_results)
                    - verified_count
                ),
                "repository_root": str(root),
            },
        )

    def verify_execution(
        self,
        execution: ExecutionIntegrationResult,
        repository_root: str | Path,
    ) -> ExecutionVerificationResult:
        return self.verify(
            execution,
            repository_root,
        )


__all__ = [
    "VerificationResult",
    "ExecutionVerificationResult",
    "CodeLibraryExecutionResultVerifier",
]
