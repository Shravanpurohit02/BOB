import ast
import difflib
from dataclasses import dataclass

from builder.patch import engine as patch_engine

from .ast_patch import ast_patch_engine


@dataclass(slots=True)
class TransactionResult:
    success: bool
    file: str
    backup: str
    diff: str
    message: str


class TransactionalPatchEngine:

    @staticmethod
    def _indent_of(text: str) -> str:
        for line in text.splitlines():
            if line.strip():
                return line[: len(line) - len(line.lstrip())]
        return ""

    @staticmethod
    def _apply_indent(source: str, indent: str) -> str:
        out = []

        for line in source.strip("\n").splitlines():
            if line.strip():
                out.append(indent + line)
            else:
                out.append("")

        return "\n".join(out)

    def apply(
        self,
        file,
        symbol,
        replacement,
        write=False,
    ):

        result = ast_patch_engine.replace(
            file=file,
            symbol=symbol,
            new_source=replacement,
        )

        if not result.success:
            return TransactionResult(
                False,
                result.file,
                "",
                "",
                result.message,
            )

        replacement = self._apply_indent(
            replacement,
            self._indent_of(result.before),
        )

        patched = result.after.replace(
            replacement.lstrip(),
            replacement,
            1,
        )

        try:
            ast.parse(patched)
        except Exception as exc:
            return TransactionResult(
                False,
                result.file,
                "",
                "",
                str(exc),
            )

        diff = "\n".join(
            difflib.unified_diff(
                result.before.splitlines(),
                replacement.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )

        backup = ""

        if write:
            try:
                patch = patch_engine.create(
                    path=result.file,
                    updated=patched,
                )

                patch_engine.commit(patch)

                # Preserve TransactionResult API.
                # Store the Patch ID in the legacy backup field.
                backup = patch.id

            except Exception as exc:
                return TransactionResult(
                    False,
                    result.file,
                    "",
                    diff,
                    str(exc),
                )

        return TransactionResult(
            True,
            result.file,
            backup,
            diff,
            "Validated" if not write else "Patched",
        )


transactional_patch_engine = TransactionalPatchEngine()
