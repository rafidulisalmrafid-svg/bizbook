import time
import httpx
from typing import Dict, Any, List, Optional
from app.services.ai.base import BaseAIProvider, AIResult
from app.config import settings

class OpenAIAdapter(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> AIResult:
        if not self.api_key:
            # Fallback to deterministic mock if API key is unconfigured
            from app.services.ai.mock_adapter import MockAIAdapter
            return await MockAIAdapter(self.model).generate_text(prompt, system_message, max_tokens, temperature)

        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message or "You are BizBook Enterprise AI."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            cost = (prompt_tokens * 0.005 / 1000) + (completion_tokens * 0.015 / 1000)
            latency_ms = int((time.time() - start_time) * 1000)

            return AIResult(
                content=content,
                provider="openai",
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
                latency_ms=latency_ms,
            )

    async def analyze_document(self, text_content: str, instructions: str) -> AIResult:
        return await self.generate_text(f"Instructions: {instructions}\n\nDocument:\n{text_content[:4000]}")

    async def extract_structured_data(self, text_content: str, expected_schema_keys: List[str]) -> AIResult:
        prompt = f"Extract the following keys as JSON: {expected_schema_keys}\n\nDocument:\n{text_content[:4000]}"
        return await self.generate_text(prompt)

    async def generate_embeddings(self, text: str) -> List[float]:
        from app.services.ai.mock_adapter import MockAIAdapter
        return await MockAIAdapter().generate_embeddings(text)

    async def summarize(self, text: str, max_length: int = 300) -> AIResult:
        return await self.generate_text(f"Summarize the following text in under {max_length} words:\n\n{text[:4000]}")
