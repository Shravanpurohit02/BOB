from builder.engineering.changeset import engine as ecs


class PipelineFinalizer:

    def finish(
        self,
        context,
    ):

        ecs.complete(
            context.changeset,
        )

        return {
            "changeset": context.changeset.id,
            "status": context.changeset.status,
        }


finalizer = PipelineFinalizer()
