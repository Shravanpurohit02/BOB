import ast
from pathlib import Path


class PatchValidator:

    def validate(self, source: str, path: str = ""):

        suffix = Path(path).suffix.lower()

        if suffix != ".py":
            return True

        try:
            ast.parse(source)
            return True
        except Exception:
            return False


validator = PatchValidator()
