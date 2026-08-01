from builder.review import engine as review

NAME = "Review"
CATEGORY = "Foundation"
DESCRIPTION = "Validates review listing and approval workflow."


def run() -> bool:

    try:
        tasks = review.list()

        if not tasks:
            return False

        task = tasks[0]

        review.approve(
            task.id,
            reviewer="regression",
        )

        refreshed = review.list()[0]

        return refreshed.status == "approved" and refreshed.reviewer == "regression"

    except Exception:
        return False
