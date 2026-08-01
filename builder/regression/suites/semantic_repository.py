from builder.ast.module import Module
from builder.context.hybrid_retrieval import engine as hybrid
from builder.context.repository_index import index
from builder.context.semantic_search import engine as semantic

NAME = "Semantic Repository"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates repository indexing and semantic retrieval."


def run() -> bool:

    try:
        repo = index.build(".")

        router = Module(
            path="providers/runtime/router.py",
        )
        router.classes.append(
            "ProviderRouter",
        )

        loader = Module(
            path="providers/runtime/loader.py",
        )
        loader.classes.append(
            "ProviderLoader",
        )

        graph = {
            "reverse": {
                "providers/runtime/router.py": ["a", "b"],
                "providers/runtime/loader.py": ["a"],
            },
            "depth": {
                "providers/runtime/router.py": 3,
                "providers/runtime/loader.py": 1,
            },
        }

        semantic_results = semantic.search(
            [router, loader],
            "provider router",
        )

        hybrid_results = hybrid.retrieve(
            [router, loader],
            graph,
            "provider router",
        )

        return (
            len(repo["python"]) > 0
            and len(semantic_results) >= 1
            and semantic_results[0].path == "providers/runtime/router.py"
            and len(hybrid_results) >= 1
            and hybrid_results[0].path == "providers/runtime/router.py"
        )

    except Exception:
        return False
