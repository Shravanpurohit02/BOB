import json
from pathlib import Path

from builder.filesystem import scanner
from builder.models.runtime import RuntimeContext

SESSION_FILE = Path(".builder/state/session.json")


def create_runtime() -> RuntimeContext:
    runtime = RuntimeContext()
    runtime.project = scanner.scan(runtime.workspace)
    return runtime


def save_session(runtime: RuntimeContext) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    SESSION_FILE.write_text(
        json.dumps(
            runtime.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )


def load_session() -> RuntimeContext:
    if SESSION_FILE.exists():
        return RuntimeContext.from_dict(
            json.loads(
                SESSION_FILE.read_text(
                    encoding="utf-8"
                )
            )
        )

    runtime = create_runtime()
    save_session(runtime)
    return runtime
