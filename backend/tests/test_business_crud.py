import pytest

@pytest.mark.asyncio
async def test_business_entities_and_portfolio_draft(client, setup_tenants):
    headers_a = setup_tenants["headers_a"]

    # 1. Create team member
    member_res = await client.post(
        "/api/v1/team",
        json={
            "full_name": "Dr. Sarah Chen",
            "email": "sarah.chen@company.com",
            "designation": "Chief AI Scientist",
            "department": "R&D",
            "skills": ["NLP", "Transformers", "RAG"],
        },
        headers=headers_a,
    )
    assert member_res.status_code == 201
    member = member_res.json()
    member_id = member["id"]

    # Add experience & certification
    exp_res = await client.post(
        f"/api/v1/team/{member_id}/experience",
        json={
            "title": "Senior AI Researcher",
            "organization": "Google DeepMind",
            "start_date": "2020-01",
            "end_date": "2023-12",
            "is_current": False,
            "description": "Architected large-scale factual retrieval systems.",
        },
        headers=headers_a,
    )
    assert exp_res.status_code == 201

    cert_res = await client.post(
        f"/api/v1/team/{member_id}/certification",
        json={
            "name": "Google Cloud Professional ML Engineer",
            "issuing_organization": "Google Cloud",
            "issue_date": "2023-05",
            "credential_id": "GCP-ML-9982",
        },
        headers=headers_a,
    )
    assert cert_res.status_code == 201

    # 2. Create Service
    service_res = await client.post(
        "/api/v1/services",
        json={
            "title": "Enterprise AI Tender Automation",
            "category": "Artificial Intelligence",
            "description": "End-to-end automated parsing and proposal generation.",
            "deliverables": ["Executive Summary", "Compliance Matrix", "Technical Proposal"],
            "typical_duration": "4 weeks",
            "standard_price": 50000.0,
        },
        headers=headers_a,
    )
    assert service_res.status_code == 201
    service = service_res.json()
    service_id = service["id"]

    # 3. Create Client
    client_res = await client.post(
        "/api/v1/clients",
        json={
            "name": "Ministry of Housing & Urban Planning",
            "industry": "Government",
            "website": "https://gov.example.com",
            "address": "Capital Administrative Complex",
        },
        headers=headers_a,
    )
    assert client_res.status_code == 201
    client_data = client_res.json()
    client_id = client_data["id"]

    # 4. Create Project
    project_res = await client.post(
        "/api/v1/projects",
        json={
            "title": "Automated Government Gateway Portal",
            "client_id": client_id,
            "service_id": service_id,
            "contract_value": 180000.0,
            "currency": "USD",
            "status": "COMPLETED",
            "completion_summary": "Delivered high-throughput citizen and official pass generator with zero downtime.",
        },
        headers=headers_a,
    )
    assert project_res.status_code == 201
    project = project_res.json()
    project_id = project["id"]

    # Link team member to project
    ptm_res = await client.post(
        f"/api/v1/projects/{project_id}/team",
        json={"team_member_id": member_id, "role_in_project": "Technical Lead"},
        headers=headers_a,
    )
    assert ptm_res.status_code == 201

    # Add evidence document
    doc_res = await client.post(
        f"/api/v1/projects/{project_id}/documents",
        json={
            "title": "Signed Completion Certificate",
            "document_url": "https://storage.bizbook.internal/evidence/comp_cert_01.pdf",
            "document_type": "COMPLETION_CERTIFICATE",
            "notes": "Verified by ministry procurement officer.",
        },
        headers=headers_a,
    )
    assert doc_res.status_code == 201

    # 5. Trigger "Create Portfolio Draft" action
    portfolio_res = await client.post(
        f"/api/v1/projects/{project_id}/portfolio-draft",
        headers=headers_a,
    )
    assert portfolio_res.status_code == 200
    portfolio_data = portfolio_res.json()
    assert portfolio_data["project_id"] == project_id
    assert "Case Study" in portfolio_data["title"]
    assert portfolio_data["evidence_count"] >= 1
    assert portfolio_data["is_ready_for_review"] is True

    # 6. Verify Audit Logs
    audit_res = await client.get("/api/v1/audit", headers=headers_a)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "portfolio.draft_created" in actions
    assert "team.member_create" in actions
