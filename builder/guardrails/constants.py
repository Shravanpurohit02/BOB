from __future__ import annotations

from .models import Severity

DEFAULT_STOP_ON_ERROR = True
DEFAULT_REPORT_ONLY = False

SEVERITY_ORDER: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.WARNING: 1,
    Severity.ERROR: 2,
    Severity.CRITICAL: 3,
}

VALIDATOR_ORDER = (
    "schema",
    "path",
    "files",
    "syntax",
    "imports",
    "duplicates",
    "api",
    "quality",
    "security",
)

FORBIDDEN_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".idea",
        ".vscode",
    }
)

FORBIDDEN_FILE_NAMES = frozenset(
    {
        ".DS_Store",
        "Thumbs.db",
    }
)

FORBIDDEN_EXTENSIONS = frozenset(
    {
        ".pyc",
        ".pyo",
        ".pyd",
        ".class",
        ".o",
        ".obj",
        ".so",
        ".dll",
        ".dylib",
        ".exe",
        ".bin",
    }
)

ALLOWED_OPERATIONS = frozenset(
    {
        "create",
        "modify",
        "delete",
        "rename",
    }
)

DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024
DEFAULT_MAX_FILES = 1000

SCHEMA_VERSION = "vidhi-builder/v1"
