from collections import defaultdict

from .reference_index import reference_indexer


class CrossReferenceEngine:

    def build(self, workspace: str):

        idx = reference_indexer.build(workspace)

        definitions = idx.definitions_by_name
        references = idx.references_by_name

        callers = defaultdict(list)
        usages = defaultdict(list)

        for name, refs in references.items():

            defs = definitions.get(name, [])

            for d in defs:
                key = f"{d.module}:{d.name}"

                for r in refs:
                    usages[key].append(r)

                    if r.module != d.module:
                        callers[key].append(r.module)

        return {
            "definitions": definitions,
            "references": references,
            "usages": usages,
            "callers": callers,
        }


cross_reference_engine = CrossReferenceEngine()
