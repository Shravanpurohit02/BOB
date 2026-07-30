from collections import defaultdict


class EngineeringKnowledgeBase:

    def __init__(self):

        self._knowledge = defaultdict(
            lambda: {
                "patterns": [],
                "failures": [],
                "successes": [],
                "metadata": {},
            }
        )

    def learn_pattern(
        self,
        category,
        pattern,
    ):

        if pattern not in self._knowledge[category]["patterns"]:
            self._knowledge[category]["patterns"].append(pattern)

    def record_success(
        self,
        category,
        item,
    ):

        self._knowledge[category]["successes"].append(item)

    def record_failure(
        self,
        category,
        item,
    ):

        self._knowledge[category]["failures"].append(item)

    def metadata(
        self,
        category,
        **values,
    ):

        self._knowledge[category]["metadata"].update(values)

    def category(
        self,
        category,
    ):

        return self._knowledge[category]

    def all(self):

        return dict(self._knowledge)


engine = EngineeringKnowledgeBase()
