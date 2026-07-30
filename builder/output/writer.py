import json
from pathlib import Path


class OutputWriter:

    def write(
        self,
        directory,
        filename,
        content,
    ):

        directory = Path(directory)
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / filename

        if isinstance(content, (dict, list)):
            path.write_text(
                json.dumps(content, indent=2),
                encoding="utf-8",
            )
        else:
            path.write_text(
                str(content),
                encoding="utf-8",
            )

        return str(path)


writer = OutputWriter()
