from builder.review.static_analysis import engine as static_analysis
from builder.review.code_quality import engine as quality
from builder.review.security import engine as security
from builder.review.performance import engine as performance
from builder.review.refactoring import engine as refactoring


class AutonomousReviewEngine:

    def review(
        self,
        source,
    ):

        static_report = static_analysis.analyze(
            source,
        )

        quality_report = quality.analyze(
            source,
        )

        security_report = security.analyze(
            source,
        )

        performance_report = performance.analyze(
            source,
        )

        refactoring_report = refactoring.analyze(
            source,
        )

        passed = (
            quality.passed(quality_report)
            and security.passed(security_report)
            and performance.passed(performance_report)
        )

        return {
            "passed": passed,
            "static": static_report,
            "quality": quality_report,
            "security": security_report,
            "performance": performance_report,
            "refactoring": refactoring_report,
        }

    def summary(
        self,
        review,
    ):

        return {
            "passed": review["passed"],
            "quality_score": review["quality"]["score"],
            "security_score": review["security"]["score"],
            "performance_score": review["performance"]["score"],
            "suggestions": review["refactoring"]["count"],
        }


engine = AutonomousReviewEngine()
