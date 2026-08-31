from builder.providers.execution.failover import RETRY_STATUS
from builder.providers.execution.retry.policy import policy


class RetryEngine:
    def attempts(self):
        return policy.max_attempts

    def should_retry(self, response=None, validation_failed=False):

        if validation_failed:
            return True

        if response is None:
            return True

        if getattr(response, "is_success", False):
            return False

        return getattr(response, "status_code", 0) in RETRY_STATUS


engine = RetryEngine()
