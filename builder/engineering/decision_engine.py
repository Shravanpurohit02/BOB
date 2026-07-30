class EngineeringDecisionEngine:

    PRIORITY = {
        "critical": 100,
        "high": 75,
        "normal": 50,
        "low": 25,
    }

    def decide(
        self,
        task,
    ):

        score = self.PRIORITY.get(
            task.get(
                "priority",
                "normal",
            ),
            50,
        )

        if task.get("repository_impact"):
            score += 20

        if task.get("architecture_change"):
            score += 15

        if task.get("breaking_change"):
            score += 30

        if task.get("new_feature"):
            score += 10

        if score >= 120:
            strategy = "architectural"

        elif score >= 80:
            strategy = "repository"

        elif score >= 60:
            strategy = "module"

        else:
            strategy = "local"

        return {
            "score": score,
            "strategy": strategy,
        }


engine = EngineeringDecisionEngine()
