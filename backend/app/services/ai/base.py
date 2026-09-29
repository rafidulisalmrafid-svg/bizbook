from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AIResult(BaseModel):
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    provider: str
    model: str
    prompt_version: str = "v1.0"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: int = 0

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> AIResult:
        pass

    @abstractmethod
    async def analyze_document(
        self,
        text_content: str,
        instructions: str,
    ) -> AIResult:
        pass

    @abstractmethod
    async def extract_structured_data(
        self,
        text_content: str,
        expected_schema_keys: List[str],
    ) -> AIResult:
        pass

    @abstractmethod
    async def generate_embeddings(
        self,
        text: str,
    ) -> List[float]:
        pass

    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int = 300,
    ) -> AIResult:
        pass
