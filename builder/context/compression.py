class ContextCompressor:

    MAX_LINE_LENGTH = 200

    def compress(self, text, budget):

        if not text:
            return ""

        lines = text.splitlines()

        result = []

        used = 0

        for line in lines:

            line = line.rstrip()

            if len(line) > self.MAX_LINE_LENGTH:
                line = line[: self.MAX_LINE_LENGTH] + "..."

            cost = max(
                1,
                len(line) // 4,
            )

            if used + cost > budget:
                break

            result.append(line)

            used += cost

        return "\n".join(result)

    def compress_files(
        self,
        files,
        budget,
    ):

        if not files:
            return []

        remaining = budget

        output = []

        for file in files:

            source = self.compress(
                file["source"],
                remaining,
            )

            cost = max(
                1,
                len(source) // 4,
            )

            if not source:
                break

            remaining -= cost

            clone = dict(file)
            clone["source"] = source

            output.append(clone)

            if remaining <= 0:
                break

        return output


compressor = ContextCompressor()
