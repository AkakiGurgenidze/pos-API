import random

from fastapi.testclient import TestClient


def get_default_product(
    unit_id: str,
    product_name: str = "Apple",
    barcode: str = "6604876475937",
    price: float = random.randint(0, 10000) / 100,
) -> dict[str, str | float]:
    return {
        "unit_id": unit_id,
        "name": product_name,
        "barcode": barcode,
        "price": price,
    }


def create_unit_and_get_id(client: TestClient) -> str:
    unit = {"name": "კგ"}
    response = client.post("/units", json=unit)
    unit_id: str = response.json()["unit"]["id"]
    return unit_id


def create_product_and_get_id(
    client: TestClient, unit_id: str, product_price: float
) -> str:
    product = get_default_product(unit_id, price=product_price)
    response = client.post("/products", json=product)
    product_id: str = response.json()["product"]["id"]
    return product_id
