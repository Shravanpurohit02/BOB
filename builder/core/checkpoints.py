import json
from dataclasses import asdict
from pathlib import Path

from builder.models.checkpoint import Checkpoint

CHECKPOINT_DIR = Path(".builder/checkpoints")

def create_checkpoint(name: str, description: str = "") -> Checkpoint:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint = Checkpoint(
        name=name,
        description=description,
    )

    (CHECKPOINT_DIR / f"{checkpoint.id}.json").write_text(
        json.dumps(asdict(checkpoint), indent=2),
        encoding="utf-8",
    )

    return checkpoint
