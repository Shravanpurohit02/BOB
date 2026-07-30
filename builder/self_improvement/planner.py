from builder.self_improvement.models import Improvement

class Planner:

    def build(self, issues):

        improvements = []

        for target, issue in issues:

            improvements.append(
                Improvement(
                    target=target,
                    issue=issue,
                    proposal=f"Resolve: {issue}",
                )
            )

        return improvements

planner = Planner()
