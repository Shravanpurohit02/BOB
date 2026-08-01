from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from builder.repository import index

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "by",
    "do",
    "exactly",
    "file",
    "files",
    "first",
    "for",
    "how",
    "in",
    "is",
    "it",
    "its",
    "name",
    "of",
    "on",
    "quote",
    "repository",
    "show",
    "that",
    "the",
    "this",
    "to",
    "what",
    "where",
    "which",
    "with",
}


@dataclass(slots=True)
class RankedFile:
    path: str
    score: float


class ContextRankingEngine:
    PATH_WEIGHT = 15.0
    NAME_WEIGHT = 30.0
    CONTENT_WEIGHT = 2.0

    def _tokens(self, text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text.lower())
            if token not in STOP_WORDS and len(token) > 1
        }

    def rank(
        self,
        workspace: str,
        objective: str,
    ) -> list[RankedFile]:

        query = self._tokens(objective)

        ranked: list[RankedFile] = []

        for item in index.files(workspace):

            if not item.is_python:
                continue

            score = 0.0

            path_lower = item.path.lower()
            stem_lower = Path(item.path).stem.lower()

            for token in query:
                score += path_lower.count(token) * self.PATH_WEIGHT
                score += stem_lower.count(token) * self.NAME_WEIGHT

            try:
                text = (
                    (Path(workspace) / item.path)
                    .read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                    .lower()
                )

                for token in query:
                    score += text.count(token) * self.CONTENT_WEIGHT

            except (OSError, UnicodeDecodeError):
                continue

            ranked.append(
                RankedFile(
                    path=item.path,
                    score=score,
                )
            )

        ranked.sort(
            key=lambda r: (
                r.score,
                r.path,
            ),
            reverse=True,
        )

        if ranked and ranked[0].score == 0:
            return ranked[:20]

        return [r for r in ranked if r.score > 0]


engine = ContextRankingEngine()
