from builder.intelligence.index import index

class Analyzer:

    def analyze(self, workspace: str):
        ctx = index.build(workspace)

        return {
            "project": ctx.project,
            "workspace": ctx.workspace,
            "files": len(ctx.files),
        }

analyzer = Analyzer()
