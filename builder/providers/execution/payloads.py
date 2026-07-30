from __future__ import annotations


class PayloadBuilder:

    def build(self, provider, request):

        api_type = getattr(provider, "api_type", "openai")

        if api_type == "gemini":
            return self._gemini(provider, request)

        if api_type == "anthropic":
            return self._anthropic(provider, request)

        return self._openai(provider, request)

    def _openai(self, provider, request):

        return {
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

    def _anthropic(self, provider, request):

        system = ""

        messages = []

        for m in request.messages:
            if m.role == "system":
                system = m.content
            else:
                messages.append(
                    {
                        "role": m.role,
                        "content": m.content,
                    }
                )

        payload = {
            "model": request.model or provider.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
        }

        if system:
            payload["system"] = system

        return payload

    def _gemini(self, provider, request):

        contents = []

        for m in request.messages:
            role = "user"

            if m.role == "assistant":
                role = "model"

            contents.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": m.content,
                        }
                    ],
                }
            )

        return {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
            },
        }


builder = PayloadBuilder()
