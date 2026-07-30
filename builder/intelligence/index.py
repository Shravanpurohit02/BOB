from builder.intelligence.context import Context
from builder.intelligence.project import project_scanner
from builder.intelligence.workspace import workspace_scanner


class ProjectIndex:

    def build(self, workspace: str):
        ctx = Context()

        ctx.workspace = workspace
        ctx.project = project_scanner.scan(workspace)
        ctx.files = workspace_scanner.scan(workspace)

        return ctx


index = ProjectIndex()
