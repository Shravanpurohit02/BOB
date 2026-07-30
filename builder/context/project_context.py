from builder.dependency import engine as deps
from builder.project import analyzer,indexer

class ProjectContext:

    def build(self,workspace):

        indexer.build(workspace)

        return {
            "summary":analyzer.summary(),
            "dependencies":deps.analyze(workspace),
        }

context=ProjectContext()
