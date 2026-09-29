import pytest
import io
from datetime import datetime, timedelta
import pypdf

def create_sample_pdf(content: str = "Corporate Registration Certificate 2024. Expiry: 2025-01-01.") -> bytes:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Add minimal PDF content
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

@pytest.mark.asyncio
async def test_document_vault_lifecycle_and_security(client, setup_tenants):
    headers_a = setup_tenants["headers_a"]           # OWNER
    headers_b = setup_tenants["headers_b"]           # OWNER B
    headers_viewer = setup_tenants["headers_viewer"] # VIEWER
    headers_member = setup_tenants["headers_member"] # MEMBER

    # 1. Company A uploads a valid PDF document
    pdf_bytes = create_sample_pdf()
    files = {"file": ("license_cert.pdf", pdf_bytes, "application/pdf")}
    data = {"category": "LEGAL"}

    upload_res = await client.post("/api/v1/documents/upload", files=files, data=data, headers=headers_a)
    assert upload_res.status_code == 201
    doc_a = upload_res.json()
    doc_a_id = doc_a["id"]
    assert doc_a["file_name"] == "license_cert.pdf"
    assert doc_a["category"] == "LEGAL"
    assert doc_a["current_version"] == 1
    assert doc_a["is_final"] is False

    # 2. Cross-tenant document isolation (IDOR): Company B cannot access doc A
    idor_get = await client.get(f"/api/v1/documents/{doc_a_id}", headers=headers_b)
    assert idor_get.status_code == 404, "Tenant B must not access Tenant A document"

    # Company B search does NOT return Company A document
    search_b = await client.get("/api/v1/documents?query=license", headers=headers_b)
    assert search_b.status_code == 200
    assert len(search_b.json()) == 0

    # 3. RBAC: VIEWER cannot delete document (requires document.delete)
    viewer_delete = await client.delete(f"/api/v1/documents/{doc_a_id}", headers=headers_viewer)
    assert viewer_delete.status_code == 403, "Viewer must be forbidden from deleting documents"

    # 4. Immutability & Versioning:
    # First, mark document as final (approved)
    finalize_res = await client.put(
        f"/api/v1/documents/{doc_a_id}",
        json={"is_final": True},
        headers=headers_a,
    )
    assert finalize_res.status_code == 200
    assert finalize_res.json()["is_final"] is True
    assert finalize_res.json()["current_version"] == 1

    # Now edit the finalized document -> rule 4: Any change creates a new version draft (v2), final is immutable
    edit_final = await client.put(
        f"/api/v1/documents/{doc_a_id}",
        json={"category": "COMPLIANCE"},
        headers=headers_a,
    )
    assert edit_final.status_code == 200
    updated_doc = edit_final.json()
    assert updated_doc["current_version"] == 2
    assert updated_doc["is_final"] is False # New version starts as mutable draft
    assert updated_doc["category"] == "COMPLIANCE"

    # 5. Expiry tracking test: Flag expired document
    past_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
    expiry_update = await client.put(
        f"/api/v1/documents/{doc_a_id}",
        json={"expiry_date": past_date},
        headers=headers_a,
    )
    assert expiry_update.status_code == 200
    assert expiry_update.json()["is_expired"] is True

    # 6. Signed URL generation & token verification
    signed_res = await client.get(f"/api/v1/documents/{doc_a_id}/signed-url", headers=headers_a)
    assert signed_res.status_code == 200
    signed_data = signed_res.json()
    assert "token=" in signed_data["signed_url"]

    # Public download using signed URL succeeds
    download_res = await client.get(signed_data["signed_url"])
    assert download_res.status_code == 200

    # Public download with invalid token fails
    invalid_download = await client.get(f"/api/v1/documents/{doc_a_id}/download?token=fake_or_expired_token")
    assert invalid_download.status_code == 403

    # 7. Template Engine: variable substitution
    tmpl_res = await client.post(
        "/api/v1/templates",
        json={
            "title": "Corporate Tender Letterhead Template",
            "category": "Tender",
            "content": "Dear {{client.name}},\n\n{{company.name}} is pleased to submit this proposal for {{project.name}} valued at {{project.value}}.\n\nSincerely,\n{{ceo.name}}, {{ceo.designation}}",
        },
        headers=headers_a,
    )
    assert tmpl_res.status_code == 201
    tmpl_id = tmpl_res.json()["id"]

    render_res = await client.post(
        f"/api/v1/templates/{tmpl_id}/render",
        json={"variables": {"client.name": "City Municipal Authority"}},
        headers=headers_a,
    )
    assert render_res.status_code == 200
    rendered_text = render_res.json()["rendered_content"]
    assert "City Municipal Authority" in rendered_text
    assert "Company A Corp" in rendered_text # grounded from company record
    assert "{{client.name}}" not in rendered_text

    # 8. Export DOCX test
    docx_export = await client.post(f"/api/v1/templates/{tmpl_id}/export-docx", headers=headers_a)
    assert docx_export.status_code == 200
    assert len(docx_export.content) > 1000 # Valid binary DOCX document
