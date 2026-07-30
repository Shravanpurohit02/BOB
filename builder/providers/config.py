from dataclasses import dataclass
import os

@dataclass(slots=True)
class ProviderConfig:
    openai_api_key: str = os.getenv("OPENAI_API_KEY","")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY","")
    groq_api_key: str = os.getenv("GROQ_API_KEY","")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY","")

config = ProviderConfig()
