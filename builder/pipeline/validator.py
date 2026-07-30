from builder.validation import engine as validation


class PipelineValidator:

    def run(
        self,
        workspace: str,
    ):

        return validation.validate(workspace)


validator = PipelineValidator()
