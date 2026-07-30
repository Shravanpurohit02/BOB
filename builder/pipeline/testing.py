from builder.testing import engine as testing


class PipelineTesting:

    def run(
        self,
        workspace: str,
    ):
        return testing.execute(workspace)


testing_pipeline = PipelineTesting()
