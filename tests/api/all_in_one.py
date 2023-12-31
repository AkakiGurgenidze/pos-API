import random

from fastapi.testclient import TestClient


def get_default_product(
    unit_id: str,
    product_name: str = "Apple",
    barcode: str = "6604876475937",
    price: int = random.randint(0, 100),
) -> dict[str, str | int]:
    return {
        "unit_id": unit_id,
        "name": product_name,
        "barcode": barcode,
        "price": price,
    }


def create_unit_and_get_id(client: TestClient) -> str:
    unit = {"name": "კგ"}
    response = client.post("/units", json=unit)
    unit_id = response.json()["unit"]["id"]
    return unit_id


def create_product_and_get_id(client, unit_id: str, product_price: int) -> str:
    product = get_default_product(unit_id, price=product_price)
    response = client.post("/products", json=product)
    product_id = response.json()["product"]["id"]
    return product_id
