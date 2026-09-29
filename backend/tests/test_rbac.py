import pytest

@pytest.mark.asyncio
async def test_rbac_permissions(client, setup_tenants):
    headers_a = setup_tenants["headers_a"]           # OWNER
    headers_viewer = setup_tenants["headers_viewer"] # VIEWER
    headers_member = setup_tenants["headers_member"] # MEMBER

    # 1. VIEWER can view company profile
    view_res = await client.get("/api/v1/company/profile", headers=headers_viewer)
    assert view_res.status_code == 200

    # 2. VIEWER cannot update company profile (requires company.edit)
    forbidden_edit = await client.put(
        "/api/v1/company/profile",
        json={"overview": "Illegal update by viewer"},
        headers=headers_viewer,
    )
    assert forbidden_edit.status_code == 403

    # 3. VIEWER cannot create a team member (requires team.edit)
    viewer_create_team = await client.post(
        "/api/v1/team",
        json={"full_name": "Ghost", "designation": "Hacker"},
        headers=headers_viewer,
    )
    assert viewer_create_team.status_code == 403

    # 4. MEMBER cannot create signature (requires signature.use)
    member_sig = await client.post(
        "/api/v1/company/signatures",
        json={
            "name": "Member Unauthorized",
            "designation": "Dev",
            "signature_image_url": "https://vault.bizbook.internal/sig1.png",
        },
        headers=headers_member,
    )
    assert member_sig.status_code == 403

    # 5. MEMBER cannot create seal (requires seal.use)
    member_seal = await client.post(
        "/api/v1/company/seals",
        json={
            "name": "Member Seal",
            "seal_image_url": "https://vault.bizbook.internal/seal.png",
        },
        headers=headers_member,
    )
    assert member_seal.status_code == 403

    # 6. OWNER can successfully create signature and seal
    owner_sig = await client.post(
        "/api/v1/company/signatures",
        json={
            "name": "Managing Director",
            "designation": "CEO",
            "signature_image_url": "https://vault.bizbook.internal/sig_ceo.png",
        },
        headers=headers_a,
    )
    assert owner_sig.status_code == 201

    owner_seal = await client.post(
        "/api/v1/company/seals",
        json={
            "name": "Official Corporate Seal",
            "seal_image_url": "https://vault.bizbook.internal/seal_corp.png",
        },
        headers=headers_a,
    )
    assert owner_seal.status_code == 201
