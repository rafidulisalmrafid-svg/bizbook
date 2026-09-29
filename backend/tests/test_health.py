import pytest

@pytest.mark.asyncio
async def test_health_endpoints(client):
    res1 = await client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "healthy"

    res2 = await client.get("/api/v1/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"
