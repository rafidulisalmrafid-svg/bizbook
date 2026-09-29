import pytest

@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # Register
    reg_payload = {
        "email": "newowner@startup.io",
        "password": "Password123!",
        "full_name": "Startup Founder",
        "company_name": "Hyper Growth Inc",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["role"] == "OWNER"
    assert reg_data["email"] == "newowner@startup.io"

    # Duplicate registration should fail
    dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # Login
    login_payload = {
        "email": "newowner@startup.io",
        "password": "Password123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # Me endpoint
    token = login_data["access_token"]
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newowner@startup.io"
