"""Framework-independent application bridge for BOB clients."""

from typing import Any

from builder.orchestrator.engine import engine
from builder.orchestrator.request import BuildRequest

from .contract import BridgeRequest, BridgeResponse
from .serialization import SerializationError, to_json_safe


class BridgeRequestError(ValueError):
    """Raised when an application bridge request is invalid."""


class ApplicationBridge:
    """Stable boundary between external clients and the BOB orchestrator."""

    def __init__(self, orchestrator_engine=None):
        self._engine = orchestrator_engine or engine

    def run(self, request: BridgeRequest | dict[str, Any]) -> BridgeResponse:
        """Execute a BOB request and return a stable response envelope."""

        normalized = self._normalize_request(request)

        try:
            normalized.validate()
        except ValueError as exc:
            raise BridgeRequestError(str(exc)) from exc

        build_request = BuildRequest(
            objective=normalized.objective.strip(),
            workspace=normalized.workspace.strip(),
            provider=normalized.provider.strip(),
            model=normalized.model.strip(),
            context=dict(normalized.context),
        )

        try:
            raw_result = self._engine.run(build_request)
            serialized = to_json_safe(raw_result)

            if not isinstance(serialized, dict):
                raise SerializationError(
                    "Orchestrator returned a non-object result"
                )

            return BridgeResponse(
                success=self._result_success(serialized),
                result=serialized,
            )

        except BridgeRequestError:
            raise
        except Exception as exc:
            return BridgeResponse(
                success=False,
                result={},
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

    @staticmethod
    def _normalize_request(
        request: BridgeRequest | dict[str, Any],
    ) -> BridgeRequest:
        if isinstance(request, BridgeRequest):
            return request

        if not isinstance(request, dict):
            raise BridgeRequestError(
                "request must be a BridgeRequest or object"
            )

        allowed = {
            "objective",
            "workspace",
            "provider",
            "model",
            "context",
        }

        unknown = sorted(set(request) - allowed)
        if unknown:
            raise BridgeRequestError(
                "unknown request fields: " + ", ".join(unknown)
            )

        try:
            return BridgeRequest(**request)
        except TypeError as exc:
            raise BridgeRequestError(str(exc)) from exc

    @staticmethod
    def _result_success(result: dict[str, Any]) -> bool:
        """Determine overall success from the existing BOB result contract."""

        for key in ("runtime", "execution", "pipeline", "generation"):
            value = result.get(key)
            if isinstance(value, dict) and value.get("success") is False:
                return False

        return True
