from builder.graph.edge import Edge
from builder.graph.node import Node

class ProjectGraph:

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        return node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def stats(self):
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }

graph = ProjectGraph()
