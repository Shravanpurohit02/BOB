import json
from dataclasses import asdict

from builder.config import settings
from builder.models.state import BuilderState

STATE_FILE = settings.state_directory / "builder_state.json"

def load_state() -> BuilderState:
    if STATE_FILE.exists():
        return BuilderState(**json.loads(STATE_FILE.read_text(encoding="utf-8")))
    return BuilderState()

def save_state(state: BuilderState) -> None:
    settings.state_directory.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(asdict(state), indent=2),
        encoding="utf-8",
    )

state = load_state()
