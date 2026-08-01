import os
from pathlib import Path

from dotenv import dotenv_values

from builder.providers.runtime.catalog import PROVIDERS
from builder.providers.runtime.config import ProviderRuntime
from builder.providers.runtime.registry import registry


class ProviderLoader:
    def __init__(self):
        self.loaded_files = []

    def _search_paths(self):
        package_root = Path(__file__).resolve().parents[3]

        return [
            Path.cwd() / ".env",
            package_root / ".env",
            Path.home() / "Vidhi-Builder/.env",
            Path.home() / "Vidhi-AI/.env",
            Path.home() / "Vidhi-AI/backend/.env",
        ]

    def load(self):

        values = {}
        self.loaded_files = []

        for env_file in self._search_paths():
            if env_file.is_file():
                values.update(dotenv_values(env_file))
                self.loaded_files.append(str(env_file))

        # Environment variables override .env values.
        values.update(os.environ)

        registry.providers.clear()

        for provider in PROVIDERS:
            prefix = provider.env_prefix

            if provider.name == "gemini":
                api_key = (
                    values.get("GEMINI_API_KEY") or values.get("GOOGLE_API_KEY") or ""
                ).strip()

                base_url = (
                    values.get("GEMINI_BASE_URL")
                    or values.get("GOOGLE_BASE_URL")
                    or provider.default_base_url
                )

                model = (
                    values.get("GEMINI_MODEL")
                    or values.get("GOOGLE_MODEL")
                    or provider.default_model
                )

            else:
                api_key = (
                    values.get(f"{prefix}_API_KEY") or values.get(f"{prefix}_KEY") or ""
                ).strip()

                base_url = values.get(f"{prefix}_BASE_URL") or provider.default_base_url

                model = values.get(f"{prefix}_MODEL") or provider.default_model

            registry.register(
                ProviderRuntime(
                    name=provider.name,
                    display_name=provider.display_name,
                    api_type=provider.api_type,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    enabled=bool(api_key),
                    healthy=bool(api_key),
                    free_tier=provider.free_tier,
                    priority=provider.priority,
                    supports_streaming=provider.supports_streaming,
                    supports_tools=provider.supports_tools,
                    supports_vision=provider.supports_vision,
                    supports_reasoning=provider.supports_reasoning,
                    supports_embeddings=provider.supports_embeddings,
                    context_window=provider.context_window,
                    max_output_tokens=provider.max_output_tokens,
                )
            )

        return registry


loader = ProviderLoader()
