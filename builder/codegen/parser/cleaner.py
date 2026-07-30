class Cleaner:

    def clean(self, code: str):

        return (
            code
            .replace("\r\n", "\n")
            .strip()
        )

cleaner = Cleaner()
