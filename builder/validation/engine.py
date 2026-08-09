from builder.validation.project import project


class ValidationEngine:

    def _summary(self, results):
        return {
            "files": len(results),
            "passed": sum(r.passed for r in results),
            "failed": sum(r.failed for r in results),
            "errors": [r for r in results if r.failed],
            "results": results,
        }

    def validate(self, workspace, transaction=None):
        return self._summary(
            project.validate(workspace)
        )


engine = ValidationEngine()

# Backward compatibility
validation = engine
