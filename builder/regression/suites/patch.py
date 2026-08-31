from pathlib import Path

from builder.patch import engine as patch

NAME = "Patch"
CATEGORY = "Foundation"
DESCRIPTION = "Validates patch creation, validation, compilation, commit and rollback."


def run() -> bool:

    tmp = Path(".builder/temp/regression_patch_test.py")
    tmp.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = "def value():\n    return 1\n"

    updated = "def value():\n    return 2\n"

    tmp.write_text(
        original,
        encoding="utf-8",
    )

    try:
        p = patch.create(
            str(tmp),
            updated,
        )

        ok = patch.validate(p) and patch.compile(p)

        if ok:
            patch.commit(p)

            ok = (
                tmp.read_text(
                    encoding="utf-8",
                )
                == updated
            )

            patch.rollback(p)

            ok = (
                ok
                and tmp.read_text(
                    encoding="utf-8",
                )
                == original
            )

        return ok

    except Exception:
        return False

    finally:
        tmp.unlink(
            missing_ok=True,
        )
