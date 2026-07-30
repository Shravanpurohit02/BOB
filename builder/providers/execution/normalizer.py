from __future__ import annotations


class ResponseNormalizer:
    """
    Normalizes responses from multiple LLM providers into a common format.
    """

    def normalize(self, provider, response):

        if response is None:
            return {
                "success": False,
                "text": "",
                "usage": {},
                "raw": {},
            }

        try:
            data = response.json()
        except Exception:
            data = {}

        text = ""

        api_type = getattr(provider, "api_type", "openai")

        try:
            if api_type == "openai":
                text = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )

            elif api_type == "anthropic":
                text = "".join(
                    part.get("text", "")
                    for part in data.get("content", [])
                    if part.get("type") == "text"
                )

            elif api_type == "gemini":
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )

            else:
                text = response.text

        except Exception:
            text = response.text

        return {
            "success": response.is_success,
            "text": text,
            "usage": data.get("usage", {}),
            "raw": data,
        }


normalizer = ResponseNormalizer()
