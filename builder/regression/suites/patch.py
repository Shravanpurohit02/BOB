from pathlib import Path

from builder.intelligence.change_executor import change_executor
from builder.patch import engine as patch


NAME = "Patch"
CATEGORY = "Foundation"
DESCRIPTION = (
    "Validates patch creation, validation, compilation, commit, rollback "
    "and AST-backed symbol deletion."
)


def _patch_lifecycle() -> bool:
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

        ok = (
            patch.validate(p)
            and patch.compile(p)
        )

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


def _delete_symbol_regression() -> bool:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        target = workspace / "greeting.py"

        original = (
            "def greet():\n"
            '    return "Hello Builder"\n'
            "\n"
            "def farewell():\n"
            '    return "Goodbye Builder"\n'
            "\n"
            "print(greet())\n"
        )

        expected = (
            "def greet():\n"
            '    return "Hello Builder"\n'
            "\n"
            "\n"
            "print(greet())\n"
        )

        target.write_text(
            original,
            encoding="utf-8",
        )

        try:
            change_executor.build(
                str(workspace)
            )

            plan = change_executor.create_plan(
                "Delete the farewell function from greeting.py"
            )

            if len(plan.operations) != 1:
                return False

            operation = plan.operations[0]

            if operation.operation != "delete_symbol":
                return False

            if operation.file != "greeting.py":
                return False

            names = {
                getattr(
                    symbol,
                    "name",
                    None,
                )
                for symbol in operation.symbols
            }

            if names != {"farewell"}:
                return False

            if len(operation.symbols) != 1:
                return False

            report = change_executor.execute(
                plan
            )

            if not report.success:
                return False

            if report.total != 1:
                return False

            if report.completed != 1:
                return False

            if report.failed != 0:
                return False

            actual = target.read_text(
                encoding="utf-8",
            )

            if actual != expected:
                return False

            if "def farewell(" in actual:
                return False

            if 'return "Goodbye Builder"' in actual:
                return False

            if "def ():" in actual:
                return False

            if "def greet(" not in actual:
                return False

            return True

        except Exception:
            return False



def run() -> bool:
    return (
        _patch_lifecycle()
        and _delete_symbol_regression()
    )
