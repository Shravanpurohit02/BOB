import httpx


class HTTPClient:
    def __init__(self, runtime, timeout: float = 120.0):

        self.runtime = runtime

        headers = {
            "Content-Type": "application/json",
        }

        api = runtime.api_type.lower()

        if api == "gemini":
            headers["x-goog-api-key"] = runtime.api_key

        elif api == "anthropic":
            headers["x-api-key"] = runtime.api_key
            headers["anthropic-version"] = "2023-06-01"

        else:
            headers["Authorization"] = f"Bearer {runtime.api_key}"

        self.client = httpx.Client(
            base_url=runtime.base_url,
            timeout=timeout,
            headers=headers,
        )

    def post(self, url, payload):

        try:
            r = self.client.post(
                url,
                json=payload,
            )

            print("=" * 80)
            print("PROVIDER :", self.runtime.name)
            print("URL      :", str(r.request.url))
            print("STATUS   :", r.status_code)
            print("=" * 80)
            print(r.text[:4000])
            print("=" * 80)

            return r

        except Exception as e:
            print(type(e).__name__, e)

            return httpx.Response(
                status_code=503,
                request=httpx.Request("POST", url),
            )

    def close(self):
        self.client.close()
