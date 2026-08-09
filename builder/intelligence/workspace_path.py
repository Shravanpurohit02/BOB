from __future__ import annotations

from pathlib import Path


class WorkspacePathError(ValueError):
    """Raised when a requested path is outside the active workspace."""


def resolve_workspace_path(
    workspace: str | Path,
    path: str | Path,
) -> Path:
    """
    Resolve an operation path against the authoritative workspace.

    Relative paths are always interpreted relative to ``workspace``.

    Absolute paths are accepted only when they are already contained
    within ``workspace``.

    The returned path is absolute, normalized, and guaranteed to remain
    inside the selected workspace.
    """

    if path is None:
        raise WorkspacePathError(
            "Target path must not be None."
        )

    raw = str(path).strip()

    if not raw:
        raise WorkspacePathError(
            "Target path must not be empty."
        )

    workspace_root = (
        Path(workspace)
        .expanduser()
        .resolve()
    )

    requested = Path(raw).expanduser()

    # ------------------------------------------------------------
    # Relative operation paths belong to the selected workspace.
    # ------------------------------------------------------------

    if not requested.is_absolute():
        target = (
            workspace_root / requested
        ).resolve()

    # ------------------------------------------------------------
    # Absolute paths are permitted only when already inside the
    # selected workspace.
    # ------------------------------------------------------------

    else:
        target = requested.resolve()

    # ------------------------------------------------------------
    # Containment check.
    #
    # Path.relative_to() provides an exact path-boundary check,
    # avoiding false positives such as:
    #
    #   /workspace
    #   /workspace-other
    # ------------------------------------------------------------

    try:
        target.relative_to(workspace_root)
    except ValueError as exc:
        raise WorkspacePathError(
            f"Path escapes workspace: {raw}"
        ) from exc

    return target


__all__ = (
    "WorkspacePathError",
    "resolve_workspace_path",
)
