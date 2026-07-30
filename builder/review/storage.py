import json
from dataclasses import asdict
from pathlib import Path

from builder.review.models import ReviewTask


class ReviewStorage:

    FILE = Path(".builder/state/review_queue.json")

    def load(self):

        if not self.FILE.exists():
            return []

        data = json.loads(
            self.FILE.read_text(
                encoding="utf-8",
            )
        )

        return [
            ReviewTask(**item)
            for item in data
        ]

    def save(self, tasks):

        self.FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.FILE.write_text(
            json.dumps(
                [
                    asdict(t)
                    for t in tasks
                ],
                indent=2,
            ),
            encoding="utf-8",
        )


storage = ReviewStorage()
