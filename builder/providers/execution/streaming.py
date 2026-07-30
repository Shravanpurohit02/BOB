from __future__ import annotations


class StreamingEngine:
    """
    Determines whether streaming should be enabled for a request.
    """

    def enabled(self, provider, request):

        if not getattr(request, "stream", False):
            return False

        return bool(
            getattr(provider, "supports_streaming", False)
        )

    def prepare_payload(self, provider, payload, request):

        payload = dict(payload)

        payload["stream"] = self.enabled(
            provider,
            request,
        )

        return payload


engine = StreamingEngine()
