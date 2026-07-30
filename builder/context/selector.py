from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.context.ranking import engine as ranking_engine


@dataclass(slots=True)
class ContextFile:
    path: str
    score: float
    content: str


class ContextSelector:

    DEFAULT_FILE_LIMIT = 20
    DEFAULT_BUDGET = 12000

    def select(
        self,
        workspace: str,
        objective: str,
        budget: int | None = None,
        max_files: int | None = None,
    ) -> list[ContextFile]:

        budget = budget or self.DEFAULT_BUDGET
        max_files = max_files or self.DEFAULT_FILE_LIMIT

        root = Path(workspace)

        selected: list[ContextFile] = []
        used = 0

        for ranked in ranking_engine.rank(workspace, objective):

            if len(selected) >= max_files:
                break

            file = root / ranked.path

            try:
                text = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            size = len(text.encode("utf-8"))

            if used + size > budget:
                break

            selected.append(
                ContextFile(
                    path=str(file.resolve()),
                    score=ranked.score,
                    content=text,
                )
            )

            used += size

        return selected

    def build_prompt_context(
        self,
        workspace: str,
        objective: str,
        budget: int | None = None,
        max_files: int | None = None,
    ) -> str:

        blocks = []

        for item in self.select(
            workspace,
            objective,
            budget,
            max_files,
        ):

            blocks.append(
                f"""### FILE: {Path(item.path).name}
Score: {item.score:.2f}

{item.content}
"""
            )

        return "\n".join(blocks)


selector = ContextSelector()
