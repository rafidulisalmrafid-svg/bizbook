from typing import Optional
from app.services.ai.base import BaseAIProvider
from app.services.ai.openai_adapter import OpenAIAdapter
from app.services.ai.mock_adapter import MockAIAdapter
from app.config import settings

class AnthropicAdapter(OpenAIAdapter):
    """Anthropic Claude adapter using unified protocol interface with mock fallback."""
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(api_key=api_key or settings.ANTHROPIC_API_KEY, model=model)

class AIFactory:
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
        p = (provider_name or settings.DEFAULT_AI_PROVIDER).lower()
        if p == "openai":
            return OpenAIAdapter()
        elif p == "anthropic":
            return AnthropicAdapter()
        return MockAIAdapter()
