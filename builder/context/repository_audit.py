from __future__ import annotations

from builder.project import analyzer, indexer
from builder.project.registry import registry
from builder.intelligence.workspace_index import workspace_indexer


class RepositoryAudit:

    MAX_FILES = 200

    def build(self, workspace: str) -> str:

        indexer.build(workspace)

        summary = analyzer.summary()
        workspace_index = workspace_indexer.build(workspace)

        parts = []

        parts.append("REPOSITORY AUDIT EVIDENCE")
        parts.append("========================")
        parts.append("")

        parts.append("PROJECT SUMMARY")
        parts.append("----------------")
        parts.append(f"Files: {summary['files']}")
        parts.append(f"Python: {summary['python']}")
        parts.append(f"JSON: {summary['json']}")
        parts.append(f"Markdown: {summary['markdown']}")
        parts.append("")

        parts.append("WORKSPACE SUMMARY")
        parts.append("-----------------")
        parts.append(f"Modules: {workspace_index.modules}")
        parts.append(f"Symbols: {workspace_index.symbols}")
        parts.append(f"Imports: {workspace_index.imports}")
        parts.append("")

        parts.append("REPOSITORY FILES")
        parts.append("----------------")

        count = 0

        for file in sorted(registry.all(), key=lambda f: f.relative_path):

            if count >= self.MAX_FILES:
                break

            parts.append(file.relative_path)
            count += 1

        return "\n".join(parts)


audit_repository = RepositoryAudit()
