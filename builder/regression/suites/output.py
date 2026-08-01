from pathlib import Path

NAME = "Output"
CATEGORY = "Foundation"
DESCRIPTION = "Validates Builder output artifacts."


def run() -> bool:

    try:
        output = Path(".builder/output")

        if not output.exists():
            return False

        for directory in output.iterdir():
            if (
                directory.is_dir()
                and (directory / "metadata.json").exists()
                and (directory / "objective.md").exists()
            ):
                return True

        return False

    except Exception:
        return False
