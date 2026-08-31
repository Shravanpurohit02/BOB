
from __future__ import annotations
import re
from pathlib import Path


class PromptCompressor:

    MAX_CONSECUTIVE_BLANKS = 1

    def _normalize_newlines(
        self,
        text: str,
    ) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        return text

    def _strip_trailing_whitespace(
        self,
        text: str,
    ) -> str:
        return "\n".join(
            line.rstrip()
            for line in text.splitlines()
        )

    def _collapse_blank_lines(
        self,
        text: str,
    ) -> str:

        output: list[str] = []
        blanks = 0

        for line in text.splitlines():

            if line.strip():
                blanks = 0
                output.append(line)
                continue

            blanks += 1

            if blanks <= self.MAX_CONSECUTIVE_BLANKS:
                output.append("")

        return "\n".join(output)

    def compress_text(
        self,
        text: str,
    ) -> str:

        text = self._normalize_newlines(text)
        text = self._strip_trailing_whitespace(text)
        text = self._collapse_blank_lines(text)

        return text.strip()

    def compress_file(
        self,
        path: str | Path,
    ) -> str:

        path = Path(path)

        return self.compress_text(
            path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )

    def compress_repository(
        self,
        files: list[str | Path],
    ) -> dict[str, str]:

        result: dict[str, str] = {}

        for file in files:
            path = Path(file)

            try:
                result[str(path)] = self.compress_file(path)
            except Exception:
                continue

        return result

    def build_prompt(
        self,
        objective: str,
        files: dict[str, str],
    ) -> str:

        sections = [
            "OBJECTIVE",
            objective.strip(),
            "",
            "REPOSITORY CONTEXT",
            "",
        ]

        for path in sorted(files):

            sections.append(f"### FILE: {path}")
            sections.append(files[path])
            sections.append("")

        return "\n".join(sections).strip()


prompt_compressor = PromptCompressor()
