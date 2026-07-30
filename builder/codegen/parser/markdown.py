import re

class MarkdownParser:

    def extract(self, text: str) -> str:

        blocks = re.findall(
            r"```(?:[a-zA-Z0-9_+-]*)\n(.*?)```",
            text,
            re.DOTALL,
        )

        if blocks:
            return "\n\n".join(blocks).strip()

        return text.strip()

parser = MarkdownParser()
