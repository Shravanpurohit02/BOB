import hashlib


class SafeModificationEngine:

    def fingerprint(
        self,
        source,
    ):

        return hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest()

    def create_patch(
        self,
        original,
        updated,
    ):

        return {
            "before": self.fingerprint(original),
            "after": self.fingerprint(updated),
            "changed": original != updated,
            "original": original,
            "updated": updated,
        }

    def validate(
        self,
        patch,
    ):

        return (
            patch["changed"]
            and patch["before"] != patch["after"]
        )

    def apply(
        self,
        patch,
    ):

        if not self.validate(patch):
            raise ValueError(
                "Invalid patch."
            )

        return patch["updated"]


engine = SafeModificationEngine()
