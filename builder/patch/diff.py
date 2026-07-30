import difflib

class DiffEngine:

    def diff(self, original: str, updated: str):

        return "".join(
            difflib.unified_diff(
                original.splitlines(True),
                updated.splitlines(True),
                fromfile="original",
                tofile="updated",
            )
        )

diff_engine = DiffEngine()
