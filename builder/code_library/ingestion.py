from __future__ import annotations

from pathlib import Path

from builder.ast.imports import imports
from builder.ast.parser import parser
from builder.context.repository_index import index as repository_index

from .engine import CodeLibraryEngine
from .models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetProvenance,
)


class CodeLibraryIngestion:
    """Production ingestion boundary for repository-derived Code Library assets."""

    def __init__(self, engine: CodeLibraryEngine | None = None) -> None:
        self.engine = engine or CodeLibraryEngine()

    def ingest_file(
        self,
        path: str,
        *,
        asset_type: str = "component",
        name: str | None = None,
        provenance: CodeAssetProvenance | None = None,
        metadata: dict | None = None,
    ) -> CodeAsset:
        source_path = Path(path).resolve()
        if not source_path.is_file():
            raise FileNotFoundError(str(source_path))

        content = source_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        module = parser.parse_source(
            source=content,
            path=str(source_path),
        )

        asset = CodeAsset(
            id=module.qualified_name or module.name or source_path.stem,
            asset_type=asset_type,
            name=name or module.name or source_path.stem,
            description=module.docstring,
            language=module.language,
            tags=list(module.tags),
            capabilities=list(module.all_symbols),
            dependencies=list(module.imports + module.import_from),
            entrypoints=list(module.exports),
            files=[
                CodeAssetFile(
                    path=module.relative_path,
                    content=content,
                    language=module.language,
                )
            ],
            provenance=provenance or CodeAssetProvenance(
                source=str(source_path),
                source_type="local_file",
                license="unknown",
                notes="Imported by BOB Code Library ingestion.",
            ),
            metadata={
                "ingestion": "file",
                "module": module.to_dict(),
                **(metadata or {}),
            },
        )

        return self.engine.register(asset)

    def ingest_workspace(
        self,
        workspace: str,
        *,
        asset_type: str = "application",
        name: str | None = None,
        provenance: CodeAssetProvenance | None = None,
        metadata: dict | None = None,
    ) -> CodeAsset:
        root = Path(workspace).resolve()
        if not root.is_dir():
            raise NotADirectoryError(str(root))

        repository = repository_index.build(str(root))
        paths = list(repository["files"])
        python_paths = list(repository["python"])

        modules = parser.parse_many(python_paths)
        dependency_graph = self._workspace_dependency_graph(
            root,
            modules,
        )

        files: list[CodeAssetFile] = []

        for raw_path in paths:
            path = Path(raw_path)

            if not path.is_file():
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except OSError:
                continue

            relative = path.relative_to(root).as_posix()

            files.append(
                CodeAssetFile(
                    path=relative,
                    content=content,
                    language=self._language(path),
                    executable=bool(path.stat().st_mode & 0o111),
                )
            )

        capabilities = sorted({
            symbol
            for module in modules
            for symbol in module.symbols
        })

        dependencies = sorted({
            dependency
            for targets in dependency_graph.values()
            for dependency in targets
        })

        entrypoints = sorted({
            symbol
            for module in modules
            for symbol in module.exports
        })

        asset = CodeAsset(
            id=root.name or "application",
            asset_type=asset_type,
            name=name or root.name or "application",
            description="Repository-ingested Code Library asset.",
            language=self._primary_language(files),
            files=files,
            capabilities=capabilities,
            dependencies=dependencies,
            entrypoints=entrypoints,
            provenance=provenance or CodeAssetProvenance(
                source=str(root),
                source_type="local_repository",
                license="unknown",
                notes="Imported by BOB Code Library ingestion.",
            ),
            metadata={
                "ingestion": "workspace",
                "workspace": str(root),
                "file_count": len(files),
                "python_file_count": len(python_paths),
                "module_count": len(modules),
                "repository": repository,
                "dependency_graph": dependency_graph,
                **(metadata or {}),
            },
        )

        return self.engine.register(asset)

    @staticmethod
    def _workspace_dependency_graph(
        root: Path,
        modules,
    ) -> dict[str, list[str]]:
        """Resolve Python imports against the workspace module namespace."""

        module_paths: dict[str, str] = {}

        for raw_path in sorted(root.rglob("*.py")):
            relative = raw_path.relative_to(root).with_suffix("")
            parts = list(relative.parts)

            if parts and parts[-1] == "__init__":
                module_name = ".".join(parts[:-1])
            else:
                module_name = ".".join(parts)

            if module_name:
                module_paths[module_name] = str(raw_path)

        graph: dict[str, list[str]] = {}

        for module in modules:
            source_path = Path(module.path)

            try:
                relative = source_path.relative_to(root).with_suffix("")
            except ValueError:
                graph[module.path] = []
                continue

            parts = list(relative.parts)

            if parts and parts[-1] == "__init__":
                module_name = ".".join(parts[:-1])
            else:
                module_name = ".".join(parts)

            dependencies: set[str] = set()

            for imported in module.imports:
                target = module_paths.get(imported)

                if target and target != module.path:
                    dependencies.add(target)

            for imported in module.import_from:
                target = module_paths.get(imported)

                if target and target != module.path:
                    dependencies.add(target)

            graph[module.path] = sorted(dependencies)

        return graph

    @staticmethod
    def _language(path: Path) -> str:
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".kt": "kotlin",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
        }.get(path.suffix.lower(), "")

    @staticmethod
    def _primary_language(files: list[CodeAssetFile]) -> str:
        languages = [item.language for item in files if item.language]
        if not languages:
            return ""
        return max(
            set(languages),
            key=languages.count,
        )


ingestion = CodeLibraryIngestion()


__all__ = (
    "CodeLibraryIngestion",
    "ingestion",
)
