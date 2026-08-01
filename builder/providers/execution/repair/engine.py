from __future__ import annotations

import json
import re


class RepairEngine:
    _FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
    _THINK = re.compile(
        r"<think>.*?</think>",
        re.IGNORECASE | re.DOTALL,
    )

    def repair(self, text: str) -> str:

        if not text:
            return ""

        text = text.replace("\ufeff", "")
        text = self._THINK.sub("", text)
        text = self._FENCE.sub("", text)

        text = text.strip()

        text = self._extract_json(text)

        text = self._remove_trailing_commas(text)

        return text.strip()

    def _extract_json(self, text: str) -> str:

        start = text.find("{")

        if start < 0:
            return text

        depth = 0

        for i in range(start, len(text)):
            c = text[i]

            if c == "{":
                depth += 1

            elif c == "}":
                depth -= 1

                if depth == 0:
                    return text[start : i + 1]

        return text[start:]

    def _remove_trailing_commas(self, text: str) -> str:

        return re.sub(
            r",(\s*[}\]])",
            r"\1",
            text,
        )

    def valid_json(self, text: str) -> bool:

        try:
            json.loads(text)
            return True
        except Exception:
            return False


engine = RepairEngine()
