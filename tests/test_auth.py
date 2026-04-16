import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_otp(client: AsyncClient):
    resp = await client.post("/v1/auth/send-otp", json={"phone": "+77001234567"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["expiresIn"] == 120


@pytest.mark.asyncio
async def test_verify_otp_success(client: AsyncClient):
    await client.post("/v1/auth/send-otp", json={"phone": "+77001234567"})
    resp = await client.post("/v1/auth/verify-otp", json={"phone": "+77001234567", "code": "1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["user"]["phone"] == "+77001234567"


@pytest.mark.asyncio
async def test_verify_otp_invalid(client: AsyncClient):
    resp = await client.post("/v1/auth/verify-otp", json={"phone": "+77001234567", "code": "0000"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post("/v1/auth/send-otp", json={"phone": "+77001234567"})
    resp = await client.post("/v1/auth/verify-otp", json={"phone": "+77001234567", "code": "1234"})
    refresh = resp.json()["refreshToken"]

    resp2 = await client.post("/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp2.status_code == 200
    assert "accessToken" in resp2.json()


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["phone"] == "+77001234567"


@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, auth_headers: dict):
    resp = await client.put("/v1/auth/role", json={"role": "seller"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
