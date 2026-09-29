import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_business_operations_proposals_invoices_and_dashboard(
    client: AsyncClient,
    setup_tenants: dict,
):
    headers_a = setup_tenants["headers_a"]
    headers_b = setup_tenants["headers_b"]
    headers_viewer = setup_tenants["headers_viewer"]

    # 1. Create a Client for Company A
    client_res = await client.post(
        "/api/v1/clients",
        headers=headers_a,
        json={
            "name": "Global Tech Corp",
            "industry": "FinTech",
            "website": "https://globaltech.example.com",
            "address": "100 Wall Street, NY",
        },
    )
    assert client_res.status_code == 201
    client_id = client_res.json()["id"]

    # 2. Create a Project for Company A
    project_res = await client.post(
        "/api/v1/projects",
        headers=headers_a,
        json={
            "client_id": client_id,
            "title": "Cloud Banking Migration",
            "category": "Cloud Infrastructure",
            "description": "Multi-region migration of core banking services to AWS and Kubernetes.",
            "budget": 250000.0,
            "status": "IN_PROGRESS",
        },
    )
    assert project_res.status_code == 201
    project_id = project_res.json()["id"]


    # 3. Create Proposal with Line Items
    proposal_payload = {
        "title": "Enterprise Cloud Architecture Proposal",
        "client_id": client_id,
        "project_id": project_id,
        "description": "Architectural overhaul and 24/7 SRE support.",
        "currency": "USD",
        "discount": 500.0,
        "tax_rate": 10.0,
        "terms_and_conditions": "Payment due within 30 days of milestone delivery.",
        "line_items": [
            {"description": "Architecture Design & Scoping", "quantity": 1.0, "unit_price": 5000.0},
            {"description": "Kubernetes Cluster Provisioning", "quantity": 2.0, "unit_price": 2500.0},
        ],
    }
    # Subtotal = 5000 + 5000 = 10000
    # Taxable = 10000 - 500 = 9500
    # Tax = 950
    # Total = 10450
    prop_res = await client.post(
        "/api/v1/operations/proposals",
        headers=headers_a,
        json=proposal_payload,
    )
    assert prop_res.status_code == 201
    prop_data = prop_res.json()
    assert prop_data["subtotal"] == 10000.0
    assert prop_data["tax_amount"] == 950.0
    assert prop_data["total_amount"] == 10450.0
    assert prop_data["status"] == "DRAFT"
    proposal_id = prop_data["id"]

    # Update proposal status to SENT
    update_res = await client.patch(
        f"/api/v1/operations/proposals/{proposal_id}",
        headers=headers_a,
        json={"status": "SENT"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "SENT"

    # 4. Create Invoice
    invoice_payload = {
        "client_id": client_id,
        "project_id": project_id,
        "proposal_id": proposal_id,
        "invoice_number": "INV-2026-001",
        "issue_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=30)),
        "currency": "USD",
        "discount": 0.0,
        "tax_rate": 10.0,
        "notes": "Milestone 1 invoice",
        "line_items": [
            {"description": "Milestone 1 Delivery", "quantity": 1.0, "unit_price": 6000.0},
        ],
    }
    # Subtotal = 6000, Tax = 600, Total = 6600
    inv_res = await client.post(
        "/api/v1/operations/invoices",
        headers=headers_a,
        json=invoice_payload,
    )
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["subtotal"] == 6000.0
    assert inv_data["tax_amount"] == 600.0
    assert inv_data["total_amount"] == 6600.0
    assert inv_data["status"] == "DRAFT"
    assert inv_data["paid_amount"] == 0.0
    invoice_id = inv_data["id"]

    # 5. Record Partial Payment
    payment1_res = await client.post(
        f"/api/v1/operations/invoices/{invoice_id}/payments",
        headers=headers_a,
        json={"amount": 2600.0},
    )
    assert payment1_res.status_code == 200
    payment1_data = payment1_res.json()
    assert payment1_data["paid_amount"] == 2600.0
    assert payment1_data["status"] == "PARTIALLY_PAID"

    # Record Final Payment
    payment2_res = await client.post(
        f"/api/v1/operations/invoices/{invoice_id}/payments",
        headers=headers_a,
        json={"amount": 4000.0},
    )
    assert payment2_res.status_code == 200
    payment2_data = payment2_res.json()
    assert payment2_data["paid_amount"] == 6600.0
    assert payment2_data["status"] == "PAID"

    # 6. Portfolio Case Study
    case_study_res = await client.post(
        "/api/v1/operations/case-studies",
        headers=headers_a,
        json={
            "project_id": project_id,
            "title": "Zero-Downtime Cloud Migration for Global Tech Corp",
            "headline": "Migrated 50+ microservices with zero customer disruption.",
            "client_display_name": "Tier-1 FinTech Institution",
            "challenge": "Legacy monolithic banking infrastructure suffering recurring downtime.",
            "solution": "Modernized architecture to multi-tenant Kubernetes and event-driven microservices.",
            "results_and_impact": "99.999% SLA achieved and 40% reduction in hosting cost.",
            "metrics": {"sla": "99.999%", "cost_reduction": "40%"},
            "is_public_approved": True,
            "technologies": ["Kubernetes", "AWS", "FastAPI", "PostgreSQL"],
        },
    )
    assert case_study_res.status_code == 201
    cs_data = case_study_res.json()
    assert cs_data["is_public_approved"] is True
    cs_id = cs_data["id"]

    # List public case studies
    public_cs_res = await client.get(
        "/api/v1/operations/case-studies?public_only=true",
        headers=headers_viewer,
    )
    assert public_cs_res.status_code == 200
    assert len(public_cs_res.json()) >= 1

    # 7. AI Social Copy Generator
    social_res = await client.post(
        "/api/v1/operations/social/generate",
        headers=headers_a,
        json={
            "project_id": project_id,
            "case_study_id": cs_id,
            "platform": "LINKEDIN",
            "tone": "thought-leadership",
        },
    )
    assert social_res.status_code == 200
    social_data = social_res.json()
    assert len(social_data["content"]) > 0
    assert len(social_data["hashtags"]) > 0
    assert social_data["platform"] == "LINKEDIN"

    # 8. Executive Dashboard Metrics
    metrics_res = await client.get(
        "/api/v1/operations/dashboard/metrics",
        headers=headers_viewer,
    )
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["total_clients"] >= 1
    assert metrics["active_projects"] >= 1
    assert metrics["open_proposals_count"] >= 1
    assert metrics["open_proposals_value"] >= 10450.0
    assert metrics["invoices_total_paid"] >= 6600.0

    # 9. RBAC Verification: VIEWER cannot create invoices
    unauth_invoice = await client.post(
        "/api/v1/operations/invoices",
        headers=headers_viewer,
        json=invoice_payload,
    )
    assert unauth_invoice.status_code == 403

    # 10. Multi-Tenant Isolation: Tenant B cannot access Tenant A's proposal or invoice
    idor_proposal = await client.get(
        f"/api/v1/operations/proposals/{proposal_id}",
        headers=headers_b,
    )
    assert idor_proposal.status_code == 404

    idor_invoice = await client.get(
        f"/api/v1/operations/invoices/{invoice_id}",
        headers=headers_b,
    )
    assert idor_invoice.status_code == 404
