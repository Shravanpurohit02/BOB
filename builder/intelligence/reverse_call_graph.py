from collections import defaultdict

from .call_graph import call_graph_builder


class ReverseCallGraphBuilder:

    def build(self, workspace: str):

        graph = call_graph_builder.build(workspace)

        reverse = defaultdict(set)

        for caller, callees in graph.items():
            for callee in callees:
                reverse[callee].add(caller)

        return reverse


reverse_call_graph_builder = ReverseCallGraphBuilder()
