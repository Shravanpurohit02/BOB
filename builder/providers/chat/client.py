from builder.providers.chat.request import ChatRequest
from builder.providers.chat.response import ChatResponse
from builder.providers.client import manager
from builder.providers.runtime import router

class ChatClient:

    def generate(self, request: ChatRequest):

        provider = router.default()
        client = manager.client(provider)

        payload = {
            "model": request.model or provider.model,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                }
                for m in request.messages
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
        }

        return ChatResponse(
            success=True,
            provider=provider.name,
            model=payload["model"],
            content="READY",
            raw=payload,
        )

chat = ChatClient()
