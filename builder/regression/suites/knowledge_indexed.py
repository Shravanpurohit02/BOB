from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.indexed import (
    IndexedKnowledgeEngine,
)


NAME = "Knowledge Indexed"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates workspace document indexing and search while preserving "
    "the validated autonomous knowledge selection layer."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            workspace = Path(directory)

            source = workspace / "backend.py"
            source.write_text(
                (
                    "Backend dependencies must not import "
                    "frontend modules.\n"
                ),
                encoding="utf-8",
            )

            unrelated = workspace / "frontend.py"
            unrelated.write_text(
                "Frontend application entry point.\n",
                encoding="utf-8",
            )

            store = KnowledgeStore()
            store.root = workspace / "knowledge"

            engine = IndexedKnowledgeEngine(store)

            indexed_count = engine.index_workspace(
                str(workspace)
            )

            documents = engine.search_documents(
                "backend dependencies"
            )

            learning = KnowledgeLearningEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-s-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Knowledge validated.",
            )

            record = learning.record(
                category="python",
                title="Backend dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                record.id,
                evidence=evidence,
            )

            learning.record_success(
                record.id,
                evidence=evidence,
            )

            knowledge = engine.prepare_knowledge(
                "backend dependency frontend modules",
                limit=10,
                verified_only=True,
            )

            document_ids = {
                item["id"]
                for item in documents.documents
            }

            knowledge_ids = {
                item["id"]
                for item in knowledge.records
            }

            return (
                indexed_count == 2
                and documents.count == 1
                and any(
                    item["path"] == str(source)
                    for item in documents.documents
                )
                and documents.documents[0]["id"]
                in document_ids
                and knowledge.count == 1
                and record.id in knowledge_ids
                and knowledge.strategy
                == "knowledge_guided_repair"
            )

    except Exception:
        return False
