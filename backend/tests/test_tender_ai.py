import pytest
import io
import zipfile
from datetime import datetime, timedelta
from app.models.tender import RequirementType, MatchingStatus

@pytest.mark.asyncio
async def test_tender_ai_lifecycle_matching_and_export(client, setup_tenants):
    headers_a = setup_tenants["headers_a"]           # OWNER
    headers_b = setup_tenants["headers_b"]           # OWNER B
    headers_viewer = setup_tenants["headers_viewer"] # VIEWER

    # 1. Company A creates a verified project and team member
    proj_res = await client.post(
        "/api/v1/projects",
        json={"title": "National High-Speed Transit ERP", "contract_value": 350000.0, "status": "COMPLETED"},
        headers=headers_a,
    )
    assert proj_res.status_code == 201

    member_res = await client.post(
        "/api/v1/team",
        json={"full_name": "Marcus Vance", "designation": "Principal Enterprise Architect", "skills": ["Cloud", "Security", "Kubernetes"]},
        headers=headers_a,
    )
    assert member_res.status_code == 201

    # 2. Company A creates a Tender
    tender_payload = {
        "title": "State Transit & Logistics Automation System",
        "reference_number": "RFP-TRAN-2026-004",
        "issuing_organization": "Department of Transportation",
        "estimated_budget": 400000.0,
        "currency": "USD",
    }
    tender_res = await client.post("/api/v1/tenders", json=tender_payload, headers=headers_a)
    assert tender_res.status_code == 201
    tender = tender_res.json()
    tender_id = tender["id"]

    # 3. Add requirements to compliance matrix
    # Req 1: Experience requirement (should MATCH the Transit ERP project)
    req1 = await client.post(
        f"/api/v1/tenders/{tender_id}/requirements",
        json={
            "section": "3.1 Past Experience",
            "requirement_text": "Demonstrated experience in Transit ERP or logistics software",
            "requirement_type": "EXPERIENCE",
            "mandatory": True,
        },
        headers=headers_a,
    )
    assert req1.status_code == 201

    # Req 2: Team requirement (should MATCH Marcus Vance)
    req2 = await client.post(
        f"/api/v1/tenders/{tender_id}/requirements",
        json={
            "section": "4.2 Key Personnel",
            "requirement_text": "Principal Enterprise Architect with Cloud and Kubernetes skills",
            "requirement_type": "TEAM",
            "mandatory": True,
        },
        headers=headers_a,
    )
    assert req2.status_code == 201

    # Req 3: Missing requirement (CMMI Level 5 Certification - DOES NOT EXIST in vault)
    req3 = await client.post(
        f"/api/v1/tenders/{tender_id}/requirements",
        json={
            "section": "5.1 Quality Audit",
            "requirement_text": "CMMI Level 5 Appraisal Certificate",
            "requirement_type": "DOCUMENT",
            "mandatory": True,
        },
        headers=headers_a,
    )
    assert req3.status_code == 201

    # 4. Trigger Matching Engine
    match_res = await client.post(f"/api/v1/tenders/{tender_id}/match", headers=headers_a)
    assert match_res.status_code == 200
    readiness = match_res.json()

    # Re-fetch tender with updated requirements
    t_after = await client.get(f"/api/v1/tenders/{tender_id}", headers=headers_a)
    assert t_after.status_code == 200
    reqs = t_after.json()["requirements"]

    # Experience match: only real project matched
    exp_req = next(r for r in reqs if r["requirement_type"] == "EXPERIENCE")
    assert exp_req["status"] == "READY"
    assert "Transit ERP" in exp_req["matched_evidence_title"]

    # Team match: verified team member matched
    team_req = next(r for r in reqs if r["requirement_type"] == "TEAM")
    assert team_req["status"] == "READY"
    assert "Marcus Vance" in team_req["matched_evidence_title"]

    # Document match: CMMI Level 5 flagged as MISSING (Zero fabrication rule!)
    doc_req = next(r for r in reqs if r["requirement_type"] == "DOCUMENT")
    assert doc_req["status"] == "MISSING"
    assert "missing" in doc_req["matching_reason"].lower()

    # Readiness validator: check blocking issue reported
    assert readiness["blocking_issues_count"] >= 1
    assert any("CMMI" in b for b in readiness["blocking_issues"])

    # 5. Generate proposal sections
    prop_res = await client.post(f"/api/v1/tenders/{tender_id}/generate-proposal", headers=headers_a)
    assert prop_res.status_code == 200
    sections = prop_res.json()
    assert len(sections) >= 5
    keys = [s["section_key"] for s in sections]
    assert "cover_letter" in keys
    assert "technical_methodology" in keys
    assert "financial_proposal" in keys

    # 6. Export structured submission ZIP package
    export_res = await client.get(f"/api/v1/tenders/{tender_id}/export-zip", headers=headers_a)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "application/zip"

    # Verify ZIP package hierarchy
    zip_bytes = export_res.content
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "01_Executive_Summary/Cover_Letter.txt" in namelist
        assert "02_Technical_Proposal/Technical_Proposal.docx" in namelist
        assert "03_Compliance_Matrix/Compliance_Matrix.csv" in namelist
        assert "04_Readiness_Report/Readiness_Assessment.txt" in namelist

    # 7. Cross-tenant isolation (IDOR): Company B cannot view or export Company A tender
    idor_tender = await client.get(f"/api/v1/tenders/{tender_id}", headers=headers_b)
    assert idor_tender.status_code == 404

    idor_export = await client.get(f"/api/v1/tenders/{tender_id}/export-zip", headers=headers_b)
    assert idor_export.status_code == 404
