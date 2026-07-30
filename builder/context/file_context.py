from pathlib import Path


class FileContext:

    MAX_LINES = 800

    def build(self, path: str):

        p = Path(path)

        if not p.exists():
            return None

        text = p.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lines = text.splitlines()

        if len(lines) > self.MAX_LINES:
            text = "\n".join(lines[:self.MAX_LINES])

        return {
            "path": str(p),
            "name": p.name,
            "suffix": p.suffix,
            "size": p.stat().st_size,
            "lines": min(len(lines), self.MAX_LINES),
            "source": text,
        }


context = FileContext()
