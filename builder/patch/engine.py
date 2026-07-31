import hashlib
import py_compile
import tempfile
from datetime import datetime, UTC
from pathlib import Path

from builder.patch.applier import applier
from builder.patch.diff import diff_engine
from builder.patch.models import Patch
from builder.patch.validator import validator
from builder.engineering.transaction.engine import engine as transactions


class PatchEngine:

    def create(
        self,
        path: str,
        updated: str,
        action: str = "modify",
    ):
        target = Path(path)

        if action == "modify" and not target.exists():
            raise RuntimeError("modify_target_missing")

        if action == "create" and target.exists():
            raise RuntimeError("create_target_exists")

        if target.exists():
            original = target.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        else:
            original = ""

        return Patch(
            path=str(target.resolve()),
            original=original,
            updated=updated,
            original_hash=hashlib.sha256(
                original.encode("utf-8")
            ).hexdigest(),
            updated_hash=hashlib.sha256(
                updated.encode("utf-8")
            ).hexdigest(),
            metadata={
                "action": action,
                "new_file": not target.exists(),
            },
        )

    def preview(
        self,
        patch: Patch,
    ):
        return diff_engine.diff(
            patch.original,
            patch.updated,
        )

    def validate(
        self,
        patch: Patch,
    ):
        patch.validated = validator.validate(
            patch.updated,
            patch.path,
        )

        return patch.validated

    def compile(
        self,
        patch: Patch,
    ):
        if Path(patch.path).suffix.lower() != ".py":
            patch.compiled = True
            return True

        fd, tmp = tempfile.mkstemp(suffix=".py")
        Path(tmp).write_text(
            patch.updated,
            encoding="utf-8",
        )

        try:
            py_compile.compile(
                tmp,
                doraise=True,
            )
            patch.compiled = True
        finally:
            Path(tmp).unlink(
                missing_ok=True,
            )

        return patch.compiled

    def commit(
        self,
        patch: Patch,
        transaction=None,
    ):

        if not self.validate(patch):
            raise RuntimeError(
                "Patch validation failed."
            )

        if not self.compile(patch):
            raise RuntimeError(
                "Patch compilation failed."
            )

        Path(patch.path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                transactions.snapshot_file(
                    transaction.transaction,
                    patch.path,
                )
            except Exception:
                pass

        applier.apply(
            patch.path,
            patch.updated,
        )

        patch.committed = True
        patch.committed_at = datetime.now(UTC).isoformat()

        return patch

    def rollback(
        self,
        patch: Patch,
    ):
        if patch.metadata.get("new_file"):
            Path(patch.path).unlink(
                missing_ok=True,
            )
        else:
            applier.apply(
                patch.path,
                patch.original,
            )

        patch.rolled_back = True
        patch.rolled_back_at = datetime.now(UTC).isoformat()

        return patch

    def apply(
        self,
        *,
        path: str,
        updated: str,
        action: str = "modify",
    ):
        patch = self.create(
            path=path,
            updated=updated,
            action=action,
        )

        self.commit(
            patch,
        )

        return patch


engine = PatchEngine()
