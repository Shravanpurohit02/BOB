from builder.providers.execution.compatibility.response import CompatibilityResponse
from builder.providers.execution.repair import engine as repair_engine


class CompatibilityEngine:
    def repair(self, provider, text: str) -> CompatibilityResponse:

        repaired = repair_engine.repair(text)

        method = getattr(
            self,
            f"_{provider.name.lower()}",
            self._default,
        )

        return method(repaired)

    def _default(self, text: str):
        return CompatibilityResponse(
            text=text.strip(),
            modified=False,
        )

    def _gemini(self, text: str):

        text = text.strip()

        #
        # Reject empty responses
        #
        if not text:
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        #
        # Reject bare JSON object
        #
        if text == "{}":
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        #
        # Recover truncated Builder JSON
        #
        if text.startswith("{") and not text.endswith("}"):
            depth = 0

            for ch in text:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1

            if depth > 0:
                text += "}" * depth

        #
        # Require Builder schema
        #
        if '"schema"' not in text:
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        return CompatibilityResponse(
            text=text,
            modified=False,
        )

    def _groq(self, text: str):

        import json

        try:
            obj = json.loads(text)
        except Exception:
            return CompatibilityResponse(
                text=text,
                modified=False,
            )

        allowed = {
            "create",
            "modify",
        }

        for f in obj.get("files", []):
            action = f.get(
                "action",
                "modify",
            )

            if action not in allowed:
                return CompatibilityResponse(
                    text="",
                    modified=True,
                )

        return CompatibilityResponse(
            text=json.dumps(
                obj,
                separators=(",", ":"),
            ),
            modified=False,
        )

    def _openrouter(self, text: str):

        import re

        text = re.sub(
            r"```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = text.replace("```", "")

        text = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

        start = text.find("{")

        if start >= 0:
            depth = 0

            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1

                elif text[i] == "}":
                    depth -= 1

                    if depth == 0:
                        text = text[start : i + 1]
                        break

        return CompatibilityResponse(
            text=text.strip(),
            modified=True,
        )

    def _nvidia(self, text: str):

        text = text.strip()

        #
        # NVIDIA occasionally returns "{}"
        #
        if text == "{}":
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        #
        # Ignore incomplete JSON
        #
        if text.startswith("{") and not text.endswith("}"):
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        #
        # Require Builder schema
        #
        if '"schema"' not in text:
            return CompatibilityResponse(
                text="",
                modified=True,
            )

        return CompatibilityResponse(
            text=text,
            modified=False,
        )

    def _mistral(self, text: str):
        return self._default(text)

    def _cerebras(self, text: str):
        return self._default(text)

    def _anthropic(self, text: str):
        return self._default(text)

    def _openai(self, text: str):
        return self._default(text)


engine = CompatibilityEngine()
