import re


class SemanticSearch:

    def _tokens(self, module):

        values = (
            module.path,
            *module.classes,
            *module.functions,
            *module.async_functions,
            *module.imports,
            *module.exports,
        )

        tokens = []

        for value in values:

            text = str(value)

            text = re.sub(
                r"([a-z])([A-Z])",
                r"\1 \2",
                text,
            )

            text = re.sub(
                r"[^A-Za-z0-9]+",
                " ",
                text,
            )

            tokens.extend(
                word.lower()
                for word in text.split()
                if word
            )

        return tokens

    def _score(self, module, query):

        query_tokens = [
            t.lower()
            for t in re.findall(
                r"[A-Za-z0-9]+",
                query,
            )
        ]

        module_tokens = self._tokens(module)

        score = 0

        for q in query_tokens:

            for token in module_tokens:

                if token == q:
                    score += 100

                elif q in token:
                    score += 25

                elif token in q:
                    score += 10

        return score

    def search(
        self,
        modules,
        query,
        limit=20,
    ):

        ranked = sorted(
            modules,
            key=lambda m: self._score(m, query),
            reverse=True,
        )

        return [
            m
            for m in ranked
            if self._score(m, query) > 0
        ][:limit]


engine = SemanticSearch()
