from __future__ import annotations

from dataclasses import dataclass

from .code_generation_integration import (
    GenerationIntegrationResult,
    GenerationRequest,
)


@dataclass(frozen=True)
class ExecutionResult:
    step_id: str
    asset_id: str
    executed: bool
    success: bool
    exit_code: int
    output: str
    error: str
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "asset_id": self.asset_id,
            "executed": self.executed,
            "success": self.success,
            "exit_code": self.exit_code,
            "output": self.output,
            "error": self.error,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ExecutionIntegrationResult:
    requirement_name: str
    results: tuple[ExecutionResult, ...]
    executed: bool
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
            "executed": self.executed,
            "successful": self.successful,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryExecutionIntegration:
    """
    Controlled execution integration for CL-15.7 generation requests.

    The default execution mode is dry-run. Actual command execution is
    opt-in and requires an explicit executor callable supplied by the
    caller. This prevents the Code Library integration layer from
    executing arbitrary generated commands implicitly.
    """

    def execute_request(
        self,
        request: GenerationRequest,
        *,
        executor=None,
        dry_run: bool = True,
    ) -> ExecutionResult:
        if not isinstance(
            request,
            GenerationRequest,
        ):
            raise TypeError(
                "request must be GenerationRequest"
            )

        if not isinstance(
            dry_run,
            bool,
        ):
            raise TypeError(
                "dry_run must be bool"
            )

        if dry_run:
            return ExecutionResult(
                step_id=request.step_id,
                asset_id=request.asset_id,
                executed=False,
                success=True,
                exit_code=0,
                output="dry_run",
                error="",
                reasons=(
                    "execution_dry_run",
                    "execution_not_performed",
                ),
                metadata={
                    "dry_run": True,
                    "executor_supplied": (
                        executor is not None
                    ),
                },
            )

        if executor is None:
            raise ValueError(
                "executor is required when dry_run=False"
            )

        if not callable(executor):
            raise TypeError(
                "executor must be callable"
            )

        try:
            raw = executor(request)

            if isinstance(raw, ExecutionResult):
                return raw

            if isinstance(raw, tuple):
                exit_code = (
                    int(raw[0])
                    if len(raw) > 0
                    else 0
                )
                output = (
                    str(raw[1])
                    if len(raw) > 1
                    else ""
                )
                error = (
                    str(raw[2])
                    if len(raw) > 2
                    else ""
                )
            else:
                exit_code = 0
                output = str(raw)
                error = ""

            success = exit_code == 0

            return ExecutionResult(
                step_id=request.step_id,
                asset_id=request.asset_id,
                executed=True,
                success=success,
                exit_code=exit_code,
                output=output,
                error=error,
                reasons=(
                    "execution_completed"
                    if success
                    else "execution_failed",
                ),
                metadata={
                    "dry_run": False,
                    "executor_supplied": True,
                },
            )

        except Exception as exc:
            return ExecutionResult(
                step_id=request.step_id,
                asset_id=request.asset_id,
                executed=True,
                success=False,
                exit_code=1,
                output="",
                error=str(exc),
                reasons=(
                    "execution_exception",
                    "execution_failed",
                ),
                metadata={
                    "dry_run": False,
                    "executor_supplied": True,
                    "exception_type": type(exc).__name__,
                },
            )

    def execute(
        self,
        generation: GenerationIntegrationResult,
        *,
        executor=None,
        dry_run: bool = True,
    ) -> ExecutionIntegrationResult:
        if not isinstance(
            generation,
            GenerationIntegrationResult,
        ):
            raise TypeError(
                "generation must be "
                "GenerationIntegrationResult"
            )

        if not generation.executable:
            return ExecutionIntegrationResult(
                requirement_name=(
                    generation.requirement_name
                ),
                results=(),
                executed=False,
                successful=False,
                score=0.0,
                reasons=(
                    "generation_not_executable",
                    "execution_blocked",
                ),
                metadata={
                    "request_count": len(
                        generation.requests
                    ),
                    "result_count": 0,
                },
            )

        results: list[ExecutionResult] = []

        for request in generation.requests:
            result = self.execute_request(
                request,
                executor=executor,
                dry_run=dry_run,
            )

            results.append(result)

            if not result.success:
                break

        successful = (
            bool(results)
            and len(results)
            == len(generation.requests)
            and all(
                result.success
                for result in results
            )
        )

        reasons = [
            "generation_requests_received",
            "execution_results_captured",
        ]

        if dry_run:
            reasons.append(
                "execution_dry_run"
            )

        if successful:
            reasons.append(
                "execution_successful"
            )
        else:
            reasons.append(
                "execution_failed"
            )

        if dry_run:
            score = 10.0 if results else 0.0
        else:
            score = (
                10.0
                if successful
                else (
                    10.0
                    * (
                        sum(
                            1
                            for result in results
                            if result.success
                        )
                        / max(
                            1,
                            len(
                                generation.requests
                            ),
                        )
                    )
                )
            )

        return ExecutionIntegrationResult(
            requirement_name=(
                generation.requirement_name
            ),
            results=tuple(results),
            executed=any(
                result.executed
                for result in results
            ),
            successful=successful,
            score=score,
            reasons=tuple(reasons),
            metadata={
                "request_count": len(
                    generation.requests
                ),
                "result_count": len(results),
                "successful_count": sum(
                    1
                    for result in results
                    if result.success
                ),
                "failed_count": sum(
                    1
                    for result in results
                    if not result.success
                ),
                "dry_run": dry_run,
            },
        )

    def execute_generation(
        self,
        generation: GenerationIntegrationResult,
        *,
        executor=None,
        dry_run: bool = True,
    ) -> ExecutionIntegrationResult:
        return self.execute(
            generation,
            executor=executor,
            dry_run=dry_run,
        )


__all__ = [
    "ExecutionResult",
    "ExecutionIntegrationResult",
    "CodeLibraryExecutionIntegration",
]
