from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path("builder")


def add_classvar_import(text: str) -> str:
    if "ClassVar" in text:
        return text

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if line.startswith("from typing import"):
            if "ClassVar" not in line:
                lines[i] = line + ", ClassVar"
            return "\n".join(lines)

    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            lines.insert(i + 1, "from typing import ClassVar")
            return "\n".join(lines)

    lines.insert(0, "from typing import ClassVar")
    return "\n".join(lines)


for path in ROOT.rglob("*.py"):
    text = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(text)
    except SyntaxError:
        continue

    replacements = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue

            if len(stmt.targets) != 1:
                continue

            target = stmt.targets[0]

            if not isinstance(target, ast.Name):
                continue

            value = stmt.value

            start = value.lineno - 1
            end = value.end_lineno
            old = "\n".join(text.splitlines()[start:end])

            new = None

            if isinstance(value, ast.List):
                new = old.replace("[", "(", 1)[::-1].replace("]", ")", 1)[::-1]

            elif isinstance(value, ast.Set):
                new = f"frozenset({old})"

            if new:
                replacements.append((old, new, target.id))

    if not replacements:
        continue

    updated = text

    for old, new, name in replacements:
        updated = updated.replace(
            f"{name} = {old}",
            f"{name}: ClassVar = {new}",
            1,
        )

    updated = add_classvar_import(updated)

    path.write_text(updated, encoding="utf-8")
    print("Updated", path)
