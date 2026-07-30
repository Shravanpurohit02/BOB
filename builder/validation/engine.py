from builder.validation.project import project


class ValidationEngine:

    def _summary(self, results):

        return {
            "files": len(results),
            "passed": sum(r.success for r in results),
            "failed": sum(not r.success for r in results),
            "errors": [
                r
                for r in results
                if not r.success
            ],
        }

    def validate(
        self,
        workspace: str,
        transaction=None,
    ):

        result = self._summary(
            project.validate(workspace)
        )

        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                transaction.transaction.validation = result
            except Exception:
                pass

        return result

    def validate_files(
        self,
        paths,
        transaction=None,
    ):

        result = self._summary(
            project.validate_files(paths)
        )

        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                transaction.transaction.validation = result
            except Exception:
                pass

        return result


engine = ValidationEngine()
