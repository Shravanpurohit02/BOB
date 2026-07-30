import json
from pathlib import Path

STATE = (
    Path.cwd()
    / ".builder"
    / "state"
    / "changesets"
)


class Storage:

    def __init__(self):

        STATE.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(self, changeset):

        target = STATE / f"{changeset['id']}.json"

        target.write_text(
            json.dumps(
                changeset,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return target

    def load(self, changeset_id):

        target = STATE / f"{changeset_id}.json"

        if not target.exists():
            return None

        return json.loads(
            target.read_text(
                encoding="utf-8",
            )
        )

    def all(self):

        result = []

        for file in sorted(
            STATE.glob("*.json")
        ):
            result.append(
                json.loads(
                    file.read_text(
                        encoding="utf-8",
                    )
                )
            )

        return result


storage = Storage()
