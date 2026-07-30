import json

from builder.providers.execution.adapter import adapter
from builder.providers.execution.endpoints import router as endpoint_router
from builder.providers.execution.failover import engine as failover
from builder.providers.execution.normalizer import normalizer
from builder.providers.execution.payloads import builder as payload_builder
from builder.providers.execution.response import ExecutionResponse
from builder.providers.execution.semantic_validator import semantic_validator
from builder.providers.execution.validator import validator


import time
from builder.providers.health import engine as health_engine
class ExecutionEngine:

    def execute(self, request):

        providers = failover.providers(adapter)

        if not providers:
            provider, _ = adapter.client()
            providers = [provider]

        failures = failover.new_failures()

        last_provider = None
        last_response = None

        for provider in providers:

            last_provider = provider

            _, client = adapter.client(provider)

            payload = payload_builder.build(
                provider,
                request,
            )

            success = False
            reason = "unknown"

            for attempt in range(
                1,
                failover.max_attempts() + 1,
            ):

                response = client.post(
                    endpoint_router.endpoint(
                        provider,
                        payload.get(
                            "model",
                            provider.model,
                        ),
                    ),
                    payload,
                )

                last_response = response

                #
                # Retryable transport / server failures
                #

                if failover.should_retry(response):

                    reason = (
                        f"http_{getattr(response,'status_code',0)}"
                    )

                    print(
                        f"[Builder] {provider.name} "
                        f"attempt {attempt}/"
                        f"{failover.max_attempts()} "
                        f"failed ({reason})"
                    )

                    if attempt < failover.max_attempts():
                        continue

                    break

                normalized = normalizer.normalize(
                    provider,
                    response,
                )

                from builder.providers.execution.compatibility import engine as compatibility

                repaired = compatibility.repair(
                    provider,
                    normalized["text"],
                )

                normalized["text"] = repaired.text

                validation = validator.validate(
                    normalized["text"]
                )

                if not validation.valid:

                    reason = validation.reason

                    print(
                        f"[Builder] Invalid response "
                        f"from {provider.name}: "
                        f"{reason}"
                    )

                    if attempt < failover.max_attempts():
                        continue

                    break

                try:
                    obj = json.loads(
                        normalized["text"]
                    )
                except Exception:

                    reason = "invalid_json"

                    if attempt < failover.max_attempts():
                        continue

                    break

                semantic = semantic_validator.validate(
                    obj
                )

                if not semantic.valid:

                    reason = semantic.reason

                    print(
                        f"[Builder] Unsafe response "
                        f"from {provider.name}: "
                        f"{reason}"
                    )

                    if attempt < failover.max_attempts():
                        continue

                    break

                success = True

                return ExecutionResponse(
                    success=True,
                    provider=provider.name,
                    model=payload.get(
                        "model",
                        provider.model,
                    ),
                    text=normalized["text"],
                    usage=normalized["usage"],
                    raw=normalized["raw"],
                )

            if not success:

                failover.record_failure(
                    failures,
                    provider,
                    failover.max_attempts(),
                    reason,
                )

        if last_provider is None:

            return ExecutionResponse(
                success=False,
                provider="",
                model="",
                text="",
                usage={},
                raw={
                    "error": "no_provider_available",
                    "failures": [],
                },
            )

        normalized = normalizer.normalize(
            last_provider,
            last_response,
        )

        return ExecutionResponse(
            success=False,
            provider=last_provider.name,
            model="",
            text=normalized["text"],
            usage=normalized["usage"],
            raw={
                "error": "all_providers_failed",
                "providers": [
                    {
                        "provider": f.provider,
                        "attempts": f.attempts,
                        "reason": f.reason,
                    }
                    for f in failures
                ],
                "last_response": normalized["raw"],
            },
        )


engine = ExecutionEngine()