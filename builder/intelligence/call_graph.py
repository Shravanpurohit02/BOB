import ast
from collections import defaultdict
from pathlib import Path


class _Visitor(ast.NodeVisitor):

    def __init__(self, module):
        self.module = module
        self.current = None
        self.calls = defaultdict(set)

    def visit_FunctionDef(self, node):
        previous = self.current
        self.current = f"{self.module}:{node.name}"
        self.generic_visit(node)
        self.current = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        if self.current:
            if isinstance(node.func, ast.Name):
                self.calls[self.current].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.calls[self.current].add(node.func.attr)
        self.generic_visit(node)


class CallGraphBuilder:

    def build(self, workspace):

        root = Path(workspace)
        graph = defaultdict(set)

        SKIP = {
            ".builder",
            "builder_backup",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "dist",
            "build",
            ".pytest_cache",
        }

        for file in root.rglob("*.py"):

            if any(part in SKIP for part in file.parts):
                continue

            try:
                tree = ast.parse(file.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue

            module = ".".join(file.relative_to(root).with_suffix("").parts)

            v = _Visitor(module)
            v.visit(tree)

            for caller, callees in v.calls.items():
                graph[caller].update(callees)

        return graph


call_graph_builder = CallGraphBuilder()
