from builder.review import engine as review

NAME = "Autonomous Review"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates autonomous review workflow."


def run() -> bool:

    try:
        tasks = review.list()

        if not tasks:
            return False

        task = tasks[0]

        review.approve(
            task.id,
            reviewer="autonomous-regression",
        )

        refreshed = review.list()[0]

        return (
            refreshed.status == "approved"
            and refreshed.reviewer == "autonomous-regression"
        )

    except Exception:
        return False
