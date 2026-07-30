from builder.deployment.manifest import manifest
from builder.deployment.packager import packager
from builder.deployment.report import report

class DeploymentEngine:

    def package(self, workspace: str):

        archive = packager.build(workspace)

        metadata = manifest.create(archive)

        return report.create(
            archive,
            metadata,
        )

engine = DeploymentEngine()
