import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from builder.engineering.changeset import engine


def main():

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

    print("CHANGESET :", ecs.id)
    print("PROJECT   :", ecs.repository.project)
    print("MODULES   :", len(ecs.repository.modules))
    print("FILES     :", len(ecs.repository.modules))
    print("RISKS     :", len(ecs.risks))


if __name__ == "__main__":
    main()
