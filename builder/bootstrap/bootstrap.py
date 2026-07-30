from builder.config import settings
from builder.constants import DIRECTORIES
from builder.core.session import create_runtime, save_session
from builder.core.state import save_state, state
from builder.filesystem import Workspace
from builder.logging import configure_logging


def bootstrap() -> None:
    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)

    Workspace(settings.workspace).mkdir()

    log = configure_logging()

    state.boot_count += 1
    state.project = settings.workspace.name
    state.workspace = str(settings.workspace)
    state.environment = settings.environment

    save_state(state)

    runtime = create_runtime()
    save_session(runtime)

    log.info("Vidhi Builder bootstrapped successfully.")
