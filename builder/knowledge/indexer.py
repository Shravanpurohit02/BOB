from pathlib import Path

from builder.knowledge.database import database
from builder.knowledge.document import Document

class Indexer:

    def build(self, workspace: str):
        count = 0

        for path in Path(workspace).rglob("*"):
            if not path.is_file():
                continue

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            database.add(
                Document(
                    path=str(path),
                    text=text,
                )
            )
            count += 1

        return count

indexer = Indexer()
