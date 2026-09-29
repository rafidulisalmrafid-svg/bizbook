import pytest

@pytest.mark.asyncio
async def test_cross_tenant_isolation(client, setup_tenants):
    headers_a = setup_tenants["headers_a"]
    headers_b = setup_tenants["headers_b"]
    comp_b = setup_tenants["company_b"]

    # 1. Company A creates a team member
    member_payload = {
        "full_name": "Alice Secret Engineer",
        "email": "alice@companya.com",
        "designation": "Principal Architect",
        "skills": ["Python", "FastAPI", "Security"],
    }
    create_res = await client.post("/api/v1/team", json=member_payload, headers=headers_a)
    assert create_res.status_code == 201
    member_a_id = create_res.json()["id"]

    # Company B tries to get Company A's member by ID (IDOR attack)
    idor_get = await client.get(f"/api/v1/team/{member_a_id}", headers=headers_b)
    assert idor_get.status_code == 404, "Tenant B must not access Tenant A member"

    # Company B tries to edit Company A's member
    idor_put = await client.put(
        f"/api/v1/team/{member_a_id}",
        json={"designation": "Hacked Designation"},
        headers=headers_b,
    )
    assert idor_put.status_code == 404, "Tenant B must not update Tenant A member"

    # Company B listing team members must NOT see Company A's member
    list_b = await client.get("/api/v1/team", headers=headers_b)
    assert list_b.status_code == 200
    ids_b = [m["id"] for m in list_b.json()]
    assert member_a_id not in ids_b

    # 2. Company A creates a client
    client_payload = {"name": "Mega Bank Corp", "industry": "Banking"}
    client_res = await client.post("/api/v1/clients", json=client_payload, headers=headers_a)
    assert client_res.status_code == 201
    client_a_id = client_res.json()["id"]

    # Company B tries to get Company A's client
    client_idor = await client.get(f"/api/v1/clients/{client_a_id}", headers=headers_b)
    assert client_idor.status_code == 404

    # 3. Company A creates a project
    project_payload = {
        "title": "Core Banking AI Modernization",
        "client_id": client_a_id,
        "contract_value": 250000.0,
        "currency": "USD",
    }
    proj_res = await client.post("/api/v1/projects", json=project_payload, headers=headers_a)
    assert proj_res.status_code == 201
    proj_a_id = proj_res.json()["id"]

    # Company B tries to read Company A's project
    proj_idor = await client.get(f"/api/v1/projects/{proj_a_id}", headers=headers_b)
    assert proj_idor.status_code == 404

    # 4. Header spoofing attack: Company A tries to pass X-Company-ID of Company B
    spoof_res = await client.get(
        "/api/v1/company",
        headers={**headers_a, "X-Company-ID": comp_b.id},
    )
    assert spoof_res.status_code == 403, "User cannot spoof membership into another company"
