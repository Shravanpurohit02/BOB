import hashlib
import time


class ContextCache:

    def __init__(self):

        self._cache = {}

    def _key(
        self,
        workspace,
        objective,
    ):

        value = f"{workspace}:{objective}"

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        workspace,
        objective,
    ):

        return self._cache.get(
            self._key(
                workspace,
                objective,
            )
        )

    def put(
        self,
        workspace,
        objective,
        value,
    ):

        self._cache[
            self._key(
                workspace,
                objective,
            )
        ] = {
            "created": time.time(),
            "value": value,
        }

        return value

    def invalidate(
        self,
        workspace=None,
        objective=None,
    ):

        if workspace is None:
            self._cache.clear()
            return

        self._cache.pop(
            self._key(
                workspace,
                objective,
            ),
            None,
        )

    def size(self):

        return len(self._cache)


cache = ContextCache()
