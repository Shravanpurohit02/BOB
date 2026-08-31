from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone
import json
from dataclasses import asdict

from builder.knowledge.audit import KnowledgeAuditEngine
from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)


NAME = "Knowledge Audit"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates autonomous knowledge governance, health reporting, "
    "stale detection and conflict detection."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            audit = KnowledgeAuditEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-j-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Knowledge validated.",
            )

            healthy = learning.record(
                category="python",
                title="Stable backend boundary",
                content=(
                    "Backend must not import frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                healthy.id,
                evidence=evidence,
            )

            learning.record_success(
                healthy.id,
            )

            stale = learning.record(
                category="python",
                title="Deprecated boundary",
                content="Use the obsolete dependency layout.",
                confidence=0.8,
                evidence=[evidence],
            )

            stale = store.get(stale.id)

            if stale is None:
                return False

            stale.updated_at = (
                datetime.now(timezone.utc)
                - timedelta(days=365)
            ).isoformat()

            store._file(stale.id).write_text(
                json.dumps(
                    asdict(stale),
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            learning.record(
                category="python",
                title="Conflicting boundary",
                content="Backend may import frontend modules.",
                confidence=0.7,
                evidence=[evidence],
            )

            learning.record(
                category="python",
                title="Conflicting boundary",
                content="Backend must not import frontend modules.",
                confidence=1.0,
                evidence=[evidence],
            )

            report = audit.audit(
                max_age_days=180,
            )

            health = audit.health(
                max_age_days=180,
            )

            return (
                report.total == 4
                and report.active >= 1
                and report.stale >= 1
                and report.conflicting >= 2
                and report.promoted >= 1
                and report.unreliable >= 1
                and len(report.records) == 4
                and health["total"] == 4
                and not health["healthy"]
            )

    except Exception:
        return False
