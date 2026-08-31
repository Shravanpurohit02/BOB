
from __future__ import annotations
from pathlib import Path


class TokenEstimator:

    CHARS_PER_TOKEN = 4

    def estimate_text(self, text: str) -> int:
        if not text:
            return 0
        return max(1, (len(text) + self.CHARS_PER_TOKEN - 1) // self.CHARS_PER_TOKEN)

    def estimate_file(self, path: str | Path) -> int:
        path = Path(path)
        return self.estimate_text(
            path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )

    def estimate_files(
        self,
        files: list[str | Path],
    ) -> int:
        return sum(
            self.estimate_file(f)
            for f in files
        )

    def estimate_bytes(
        self,
        text: str,
    ) -> int:
        return len(
            text.encode("utf-8")
        )

    def fits(
        self,
        *,
        tokens: int,
        bytes_: int,
        profile,
    ) -> bool:
        return (
            tokens <= profile.usable_input_tokens
            and
            bytes_ <= profile.max_request_bytes
        )


token_estimator = TokenEstimator()
