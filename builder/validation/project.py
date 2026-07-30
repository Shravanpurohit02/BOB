from pathlib import Path

from builder.validation.python import validator


class ProjectValidator:

    def validate_files(self, paths):

        results = []

        for path in paths:

            path = Path(path)

            if not path.exists():
                continue

            if path.suffix != ".py":
                continue

            results.append(
                validator.validate(path)
            )

        return results

    def validate(self, workspace: str):

        files = [
            str(f)
            for f in Path(workspace).rglob("*.py")
        ]

        return self.validate_files(files)


project = ProjectValidator()
