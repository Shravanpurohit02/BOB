from builder.providers.runtime.loader import loader
from builder.providers.runtime.router import router

NAME = "Provider Runtime"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates provider runtime registry and routing."


def run() -> bool:

    try:
        registry = loader.load()

        providers = registry.all()

        ok = (
            len(providers) > 0
            and registry.get("groq") is not None
            and isinstance(registry.enabled(), list)
            and isinstance(registry.free(), list)
            and isinstance(registry.supports("streaming"), list)
            and {p.name for p in router.available()}
            == {p.name for p in registry.enabled()}
        )

        best = router.default()

        if registry.enabled():
            ok = ok and (best is not None)

        return ok

    except Exception:
        return False
