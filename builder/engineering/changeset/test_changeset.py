import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builder.engineering.changeset import engine


def run():
    ecs = engine.create(
        objective="Engineering Context Integration Test",
        workspace=str(ROOT.parent),
    )

    engine.add_file(
        ecs,
        ".builder/builder/engineering/context/engine.py",
        "modify",
        "Context integration",
    )

    engine.add_risk(
        ecs,
        "low",
        "Context",
        "Engineering context generated",
    )

    engine.report(
        ecs,
        "Engineering context successfully attached.",
        recommendations=[
            "Proceed to B-01.4",
        ],
    )

    engine.save(ecs)

    return (
        bool(ecs.id)
        and ecs.repository is not None
        and len(ecs.repository.modules) >= 0
        and len(ecs.risks) == 1
    )


def test_changeset():
    assert run()
