from builder.patch import engine as patch_engine
from builder.review import engine as review_engine


class ReviewApplier:

    def apply(
        self,
        task_id: str,
        updated_source: str,
    ):

        tasks = review_engine.list()

        task = next(
            (
                t for t in tasks
                if t.id == task_id
            ),
            None,
        )

        if task is None:
            raise RuntimeError(
                "Review task not found."
            )

        if task.status != "approved":
            raise RuntimeError(
                "Review task is not approved."
            )

        patch = patch_engine.create(
            task.target,
            updated_source,
        )

        patch_engine.commit(
            patch,
        )

        task.status = "applied"

        return patch


applier = ReviewApplier()
