from builder.providers.chat.messages import Message
from builder.providers.execution.endpoints import router as endpoint_router
from builder.providers.execution.failover import engine as failover
from builder.providers.execution.normalizer import normalizer
from builder.providers.execution.payloads import builder as payload_builder
from builder.providers.execution.streaming import engine as streaming

NAME = "Provider Execution"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates provider payload generation, routing, normalization and failover."
)


def run() -> bool:

    try:

        class Provider:
            def __init__(self, api_type):

                self.api_type = api_type
                self.model = "demo-model"
                self.supports_streaming = True

        class Request:
            model = ""
            temperature = 0.2
            max_tokens = 128
            stream = True

            messages = [
                Message(
                    role="user",
                    content="hello",
                )
            ]

        request = Request()

        openai = payload_builder.build(
            Provider("openai"),
            request,
        )

        anthropic = payload_builder.build(
            Provider("anthropic"),
            request,
        )

        gemini = payload_builder.build(
            Provider("gemini"),
            request,
        )

        endpoint = endpoint_router.endpoint(
            Provider("openai"),
            "demo-model",
        )

        class Response:
            is_success = True
            status_code = 200
            text = "hello"

            def json(self):

                return {
                    "choices": [
                        {
                            "message": {
                                "content": "hello",
                            }
                        }
                    ],
                    "usage": {},
                }

        normalized = normalizer.normalize(
            Provider("openai"),
            Response(),
        )

        return (
            "messages" in openai
            and "messages" in anthropic
            and anthropic["messages"][0]["role"] == "user"
            and "contents" in gemini
            and endpoint == "/chat/completions"
            and normalized["text"] == "hello"
            and streaming.enabled(
                Provider("openai"),
                request,
            )
            and failover.should_retry(
                type(
                    "Retry",
                    (),
                    {
                        "is_success": False,
                        "status_code": 429,
                    },
                )()
            )
        )

    except Exception:
        return False
