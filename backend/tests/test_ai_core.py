import pytest

@pytest.mark.asyncio
async def test_ai_core_and_rag_grounding(client, setup_tenants):
    headers_a = setup_tenants["headers_a"] # Company A Owner
    headers_b = setup_tenants["headers_b"] # Company B Owner
    headers_viewer = setup_tenants["headers_viewer"] # VIEWER

    # 1. Company A generates document with a missing certificate
    gen_payload = {
        "document_type": "TENDER_TECHNICAL_PROPOSAL",
        "user_instruction": "Generate proposal for Smart City Infrastructure with ISO 27001 compliance.",
        "required_certifications": ["ISO 27001", "CMMI Level 3"],
    }
    gen_res = await client.post("/api/v1/ai/generate-document", json=gen_payload, headers=headers_a)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()

    # Rule 7 Check: Missing certificates MUST be reported explicitly under missing_information, NOT fabricated
    assert len(gen_data["missing_information"]) >= 2
    missing_texts = " ".join(gen_data["missing_information"])
    assert "ISO 27001" in missing_texts
    assert "CMMI Level 3" in missing_texts
    assert "Missing" in missing_texts

    # Rule 8 Check: Financial / legal review warning attached
    assert any("human review" in w.lower() for w in gen_data["warnings"])

    # Document content is NOT empty
    assert len(gen_data["content"]) > 20
    assert len(gen_data["sections"]) > 0

    # Token and cost tracking logged
    assert "token_usage" in gen_data
    assert gen_data["token_usage"]["total_tokens"] > 0

    # 2. Check Usage and Quotas Endpoint
    usage_res = await client.get("/api/v1/ai/usage", headers=headers_a)
    assert usage_res.status_code == 200
    usage_data = usage_res.json()
    assert usage_data["tokens_consumed"] > 0
    assert len(usage_data["recent_logs"]) > 0
    assert usage_data["recent_logs"][0]["operation"] == "generate_TENDER_TECHNICAL_PROPOSAL"

    # 3. Cross-Tenant Memory Isolation (Rule 3):
    # Company A creates a proprietary project
    await client.post(
        "/api/v1/projects",
        json={"title": "Company A Secret Quantum AI Defense System", "contract_value": 900000.0},
        headers=headers_a,
    )

    # Company B queries AI memory
    query_b = await client.post(
        "/api/v1/ai/ask-memory",
        json={"query": "List all our defense systems and projects"},
        headers=headers_b,
    )
    assert query_b.status_code == 200
    answer_b = query_b.json()["answer"]
    # Company B must NEVER see Company A's secret project
    assert "Secret Quantum AI Defense System" not in answer_b

    # 4. RBAC Check: VIEWER cannot trigger generation (requires tender.create)
    viewer_gen = await client.post(
        "/api/v1/ai/generate-document",
        json=gen_payload,
        headers=headers_viewer,
    )
    assert viewer_gen.status_code == 403, "Viewer cannot trigger AI proposal generation"
