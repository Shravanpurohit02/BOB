from pathlib import Path

from builder.testing.report import report
from builder.testing.runner import runner
from builder.testing.testcase import TestCase
from builder.validation import engine as validator


class TestingEngine:

    def _run(self, validation_callable, workspace_check):

        tests = [

            TestCase(
                "python_validation",
                validation_callable,
            ),

            TestCase(
                "workspace_exists",
                workspace_check,
            ),

        ]

        return report.create(
            runner.run(tests)
        )

    def execute(
        self,
        workspace: str,
        transaction=None,
    ):

        return self._run(
            lambda: validator.validate(
                workspace,
                transaction=transaction,
            ),
            lambda: Path(workspace).exists()
            or (_ for _ in ()).throw(
                RuntimeError("Workspace missing")
            ),
        )

    def execute_files(
        self,
        paths,
        transaction=None,
    ):

        return self._run(
            lambda: validator.validate_files(
                paths,
                transaction=transaction,
            ),
            lambda: True,
        )


engine = TestingEngine()
