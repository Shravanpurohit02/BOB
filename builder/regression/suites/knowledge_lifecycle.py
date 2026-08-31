from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone

from builder.knowledge.core import (
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.lifecycle import (
    KnowledgeLifecycleEngine,
)


NAME = "Knowledge Lifecycle"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates stale knowledge detection, conflict detection, "
    "supersession and active-state evaluation."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            lifecycle = KnowledgeLifecycleEngine(store)

            active = learning.record(
                category="python",
                title="Stable dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                confidence=1.0,
            )

            active = store.get(active.id)

            if active is None:
                return False

            active.updated_at = datetime.now(
                timezone.utc
            ).isoformat()

            store.save(active)

            active = store.get(active.id)

            if active is None:
                return False

            active_state = lifecycle.evaluate(
                active,
                max_age_days=180,
            )

            stale = learning.record(
                category="python",
                title="Old dependency rule",
                content=(
                    "Use the deprecated dependency layout."
                ),
                confidence=0.8,
            )

            stale = store.get(stale.id)

            if stale is None:
                return False

            stale.updated_at = (
                datetime.now(timezone.utc)
                - timedelta(days=365)
            ).isoformat()

            # Directly persist the historical timestamp without
            # invoking KnowledgeStore.save(), which refreshes updated_at.
            stale_file = store._file(stale.id)
            import json
            from dataclasses import asdict

            stale_file.write_text(
                json.dumps(
                    asdict(stale),
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            stale = store.get(stale.id)

            if stale is None:
                return False

            stale_state = lifecycle.evaluate(
                stale,
                max_age_days=180,
            )

            conflict_a = learning.record(
                category="python",
                title="Runtime dependency policy",
                content="Backend may import frontend modules.",
                confidence=0.6,
            )

            conflict_b = learning.record(
                category="python",
                title="Runtime dependency policy",
                content="Backend must not import frontend modules.",
                confidence=1.0,
            )

            conflict_a = store.get(conflict_a.id)

            if conflict_a is None:
                return False

            conflict_state = lifecycle.evaluate(
                conflict_a,
                max_age_days=180,
            )

            superseded = lifecycle.supersede(
                stale.id
            )

            return (
                active_state.active
                and not active_state.stale
                and not active_state.conflicting
                and stale_state.stale
                and stale_state.superseded
                and not stale_state.active
                and conflict_state.conflicting
                and conflict_state.superseded
                and not conflict_state.active
                and superseded is not None
                and not superseded.promoted
                and superseded.confidence == 0.25
            )

    except Exception:
        return False
