import pytest
from httpx import AsyncClient


async def _create_seller_with_product(client: AsyncClient, auth_headers: dict) -> int:
    """Helper: make current user a seller and create a product."""
    await client.put("/v1/auth/role", json={"role": "seller"}, headers=auth_headers)
    resp = await client.post("/v1/products", json={
        "name": "Order Test Beef",
        "category": "Мясо",
        "price": 2800,
        "wholesalePrice": 2600,
        "unit": "кг",
        "stock": 100,
        "minOrder": 1,
    }, headers=auth_headers)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, auth_headers: dict):
    product_id = await _create_seller_with_product(client, auth_headers)

    # Switch to buyer to create order
    await client.put("/v1/auth/role", json={"role": "buyer"}, headers=auth_headers)

    resp = await client.post("/v1/orders", json={
        "items": [{"productId": product_id, "quantity": 5}],
        "deliveryType": "pickup",
        "paymentMethod": "cash",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["status"] == "new"


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient, auth_headers: dict):
    product_id = await _create_seller_with_product(client, auth_headers)
    await client.put("/v1/auth/role", json={"role": "buyer"}, headers=auth_headers)

    await client.post("/v1/orders", json={
        "items": [{"productId": product_id, "quantity": 2}],
        "deliveryType": "delivery",
        "paymentMethod": "kaspi",
        "address": "ул. Тараз 1",
    }, headers=auth_headers)

    resp = await client.get("/v1/orders", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
