class IncrementalCodeEvolution:

    def evolve(
        self,
        current_version,
        modifications,
    ):

        history = []

        version = current_version

        for index, modification in enumerate(
            modifications,
            start=1,
        ):

            history.append(
                {
                    "revision": index,
                    "version": version,
                    "change": modification,
                }
            )

            version += 1

        return {
            "initial_version": current_version,
            "current_version": version,
            "history": history,
        }

    def latest(
        self,
        evolution,
    ):

        history = evolution["history"]

        return (
            history[-1]
            if history
            else None
        )

    def revisions(
        self,
        evolution,
    ):

        return len(
            evolution["history"]
        )


engine = IncrementalCodeEvolution()
