from pathlib import Path

from builder.engineering.transaction.engine import engine as transactions

NAME = "Transaction"
CATEGORY = "Foundation"
DESCRIPTION = "Validates transaction snapshot and rollback."


def run() -> bool:

    try:
        tmp = Path(".builder/temp/transaction_test.txt")

        tmp.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        original = "original"
        updated = "modified"

        tmp.write_text(
            original,
            encoding="utf-8",
        )

        tx = transactions.begin(
            objective="Regression",
            workspace=".",
        )

        transactions.snapshot_file(
            tx,
            str(tmp),
        )

        tmp.write_text(
            updated,
            encoding="utf-8",
        )

        transactions.rollback(
            tx,
        )

        ok = (
            tmp.read_text(
                encoding="utf-8",
            )
            == original
        )

        tmp.unlink(
            missing_ok=True,
        )

        return ok

    except Exception:
        return False
