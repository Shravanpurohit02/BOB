import json
import re


class JSONParser:

    def _extract_json(self, text: str) -> str:

        text = text.strip()

        # Remove Markdown fences.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        decoder = json.JSONDecoder()

        for i, ch in enumerate(text):

            if ch != "{":
                continue

            try:
                obj, end = decoder.raw_decode(text[i:])
                return json.dumps(obj)
            except Exception:
                pass

        return text

    def parse(self, raw):

        if isinstance(raw, dict):
            return raw

        cleaned = self._extract_json(raw)

        return json.loads(cleaned)


parser = JSONParser()
