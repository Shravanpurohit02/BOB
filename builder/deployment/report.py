from builder.deployment.artifact import Artifact

class DeploymentReport:

    def create(self, archive, metadata):

        return Artifact(
            name=metadata["name"],
            path=archive,
            size=metadata["size"],
        )

report = DeploymentReport()
