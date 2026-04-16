import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_products(client: AsyncClient, auth_headers: dict):
    # First become a seller
    await client.put("/v1/auth/role", json={"role": "seller"}, headers=auth_headers)

    # Create product
    resp = await client.post("/v1/products", json={
        "name": "Test Beef",
        "category": "Мясо",
        "price": 2800,
        "unit": "кг",
        "stock": 100,
    }, headers=auth_headers)
    assert resp.status_code == 201
    product_id = resp.json()["id"]

    # List products
    resp2 = await client.get("/v1/products")
    assert resp2.status_code == 200
    assert resp2.json()["total"] >= 1

    # Get single product
    resp3 = await client.get(f"/v1/products/{product_id}")
    assert resp3.status_code == 200
    assert resp3.json()["name"] == "Test Beef"


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, auth_headers: dict):
    await client.put("/v1/auth/role", json={"role": "seller"}, headers=auth_headers)

    resp = await client.post("/v1/products", json={
        "name": "To Update",
        "category": "Мясо",
        "price": 1000,
        "unit": "кг",
    }, headers=auth_headers)
    pid = resp.json()["id"]

    resp2 = await client.put(f"/v1/products/{pid}", json={"price": 1500}, headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json()["price"] == 1500


@pytest.mark.asyncio
async def test_delete_product_soft(client: AsyncClient, auth_headers: dict):
    await client.put("/v1/auth/role", json={"role": "seller"}, headers=auth_headers)

    resp = await client.post("/v1/products", json={
        "name": "To Delete",
        "category": "Мясо",
        "price": 500,
        "unit": "кг",
    }, headers=auth_headers)
    pid = resp.json()["id"]

    resp2 = await client.delete(f"/v1/products/{pid}", headers=auth_headers)
    assert resp2.status_code == 200

    # Product should no longer appear in active list
    resp3 = await client.get(f"/v1/products/{pid}")
    assert resp3.json()["isActive"] is False
