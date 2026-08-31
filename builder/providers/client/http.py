from __future__ import annotations

import httpx


class HTTPClient:
    def __init__(self, runtime, timeout: float = 120.0):

        if runtime is None:
            raise ValueError("Provider runtime is required")

        base_url = str(
            getattr(runtime, "base_url", "") or ""
        ).strip()

        if not base_url:
            raise ValueError(
                f"Provider {getattr(runtime, 'name', '')!r} "
                "has no base URL"
            )

        api_key = str(
            getattr(runtime, "api_key", "") or ""
        ).strip()

        if not api_key:
            raise ValueError(
                f"Provider {getattr(runtime, 'name', '')!r} "
                "has no API credential"
            )

        self.runtime = runtime

        headers = {
            "Content-Type": "application/json",
        }

        api = str(
            getattr(runtime, "api_type", "openai") or "openai"
        ).strip().lower()

        if api == "gemini":
            headers["x-goog-api-key"] = api_key

        elif api == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"

        else:
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=headers,
        )

    def post(self, url, payload):

        try:
            endpoint = str(url or "").strip()

            if not endpoint:
                raise ValueError(
                    f"Empty endpoint for provider "
                    f"{self.runtime.name}"
                )

            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            response = self.client.post(
                endpoint,
                json=payload,
            )

            print("=" * 80)
            print("PROVIDER :", self.runtime.name)
            print("URL      :", str(response.request.url))
            print("STATUS   :", response.status_code)
            print("=" * 80)
            print(response.text[:4000])
            print("=" * 80)

            return response

        except Exception as exc:

            print("=" * 80)
            print("PROVIDER :", self.runtime.name)
            print("TRANSPORT ERROR :", type(exc).__name__)
            print("MESSAGE :", str(exc))
            print("=" * 80)

            request = httpx.Request(
                "POST",
                str(url or ""),
            )

            return httpx.Response(
                status_code=503,
                request=request,
                json={
                    "error": {
                        "type": "transport_error",
                        "exception": type(exc).__name__,
                        "message": str(exc),
                    }
                },
            )

    def close(self):
        self.client.close()
