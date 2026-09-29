import time
import json
from typing import Dict, Any, List, Optional
from app.services.ai.base import BaseAIProvider, AIResult

class MockAIAdapter(BaseAIProvider):
    def __init__(self, model_name: str = "mock-gpt-4o"):
        self.model_name = model_name

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> AIResult:
        start_time = time.time()
        
        # Check if prompt asks for missing credentials
        lowered = prompt.lower()
        missing_info = []
        warnings = []

        if "iso 27001" in lowered and "iso 27001 missing" in lowered:
            missing_info.append("ISO 27001 Information Security Certification is MISSING from company records.")

        if "financial" in lowered or "budget" in lowered or "price" in lowered:
            warnings.append("AI-generated financial and legal data is marked: NEEDS HUMAN REVIEW. Monetary values require authorized approval.")

        content = f"[BizBook Grounded Output]\nBased strictly on retrieved records:\n"
        if "tender" in lowered or "proposal" in lowered:
            content += "Executive Proposal grounded in verified past performance.\n"
            content += "All technical deliverables are aligned with company capabilities."

        prompt_tokens = len(prompt.split()) + 30
        completion_tokens = len(content.split()) + 20
        total_tokens = prompt_tokens + completion_tokens
        # $0.005 per 1K tokens
        estimated_cost = (total_tokens / 1000.0) * 0.005
        latency_ms = int((time.time() - start_time) * 1000) + 15

        structured = {
            "title": "Generated Grounded Proposal Document",
            "warnings": warnings,
            "missing_information": missing_info,
        }

        return AIResult(
            content=content,
            structured_data=structured,
            provider="mock",
            model=self.model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round(estimated_cost, 6),
            latency_ms=latency_ms,
        )

    async def analyze_document(
        self,
        text_content: str,
        instructions: str,
    ) -> AIResult:
        start_time = time.time()
        prompt_tokens = len(text_content.split()) + len(instructions.split())
        completion_tokens = 50
        total_tokens = prompt_tokens + completion_tokens
        latency_ms = int((time.time() - start_time) * 1000) + 20

        analysis = {
            "summary": f"Document analyzed with {len(text_content)} characters.",
            "compliance_detected": True,
            "keywords": ["Compliance", "Contract", "Verified"],
        }

        return AIResult(
            content=json.dumps(analysis),
            structured_data=analysis,
            provider="mock",
            model=self.model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round((total_tokens / 1000.0) * 0.005, 6),
            latency_ms=latency_ms,
        )

    async def extract_structured_data(
        self,
        text_content: str,
        expected_schema_keys: List[str],
    ) -> AIResult:
        data = {k: f"Extracted value for {k}" for k in expected_schema_keys}
        return AIResult(
            content=json.dumps(data),
            structured_data=data,
            provider="mock",
            model=self.model_name,
            prompt_tokens=len(text_content.split()),
            completion_tokens=len(expected_schema_keys) * 10,
            total_tokens=len(text_content.split()) + len(expected_schema_keys) * 10,
            estimated_cost_usd=0.0001,
            latency_ms=25,
        )

    async def generate_embeddings(self, text: str) -> List[float]:
        # Return deterministic 128-dimensional embedding vector
        length = len(text)
        return [float((i + length) % 100) / 100.0 for i in range(128)]

    async def summarize(self, text: str, max_length: int = 300) -> AIResult:
        words = text.split()[:40]
        summary_text = " ".join(words) + "..."
        return AIResult(
            content=summary_text,
            structured_data={"summary": summary_text},
            provider="mock",
            model=self.model_name,
            prompt_tokens=len(words),
            completion_tokens=len(words),
            total_tokens=len(words) * 2,
            estimated_cost_usd=0.00005,
            latency_ms=18,
        )
