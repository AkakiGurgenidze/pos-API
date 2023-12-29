import random
from unittest.mock import ANY
from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def get_product(unit_id: UUID, product_name: str = "Apple", barcode: str = '6604876475937',
                price: int = random.randint(0, 100)):
    return {
        "unit_id": unit_id,
        "name": product_name,
        "barcode": barcode,
        "price": price
    }


def get_unit_id(client):
    unit = {
        "name": "კგ"
    }
    response = client.post("/units", json=unit)
    unit_id = response.json()["unit"]["id"]
    return unit_id


def test_should_create_product(client: TestClient) -> None:
    unit_id = get_unit_id(client)

    product = get_product(unit_id)
    response = client.post("/products", json=product)

    assert response.status_code == 201
    assert response.json() == {"product": {"id": ANY, **product}}


def test_should_not_create_product_that_exists(client: TestClient) -> None:
    unit_id = get_unit_id(client)

    product = get_product(unit_id)
    client.post("/products", json=product)
    response = client.post("/products", json=product)

    assert response.status_code == 409
    assert response.json() == {"error": {"message": f"Product with barcode<{product['barcode']}> already exists."}}


# def test_should_not_create_without_unit(client: TestClient) -> None:
#     product = get_product(uuid4())
#     client.post("/products", json=product)
#     response = client.post("/products", json=product)
#
#     assert response.status_code == 409
#     assert response.json() == {"error": {"message": f"Product with barcode<{product['barcode']}> already exists."}}


def test_should_not_read_unknown_product(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {"error": {"message": f"Product with id<{unknown_id}> does not exist."}}


def test_should_persist_product(client: TestClient):
    unit_id = get_unit_id(client)

    product = get_product(unit_id)
    response = client.post("/products", json=product)
    product_id = response.json()['product']['id']
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == {"product": {"id": product_id, **product}}


def test_get_all_products_on_empty(client: TestClient):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": []}


def test_get_all_products(client: TestClient):
    unit_id = get_unit_id(client)

    product = get_product(unit_id)
    response = client.post("/products", json=product)
    product_id = response.json()['product']['id']

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": [{"id": product_id, **product}]}


def test_update_product_price(client: TestClient):
    unit_id = get_unit_id(client)

    product = get_product(unit_id, "Bread", '123456789', 10)
    response = client.post("/products", json=product)
    product_id = response.json()['product']['id']
    new_price = 20
    response = client.patch(f'/products/{product_id}/{new_price}')

    assert response.status_code == 200
    assert response.json() == {}

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == {"product": {"id": product_id, **product, "price": new_price}}


def test_should_not_update_unknown_product(client: TestClient):
    unknown_id = uuid4()
    new_price = 20
    response = client.patch(f'/products/{unknown_id}/{new_price}')

    assert response.status_code == 404
    assert response.json() == {"error": {"message": f"Product with id<{unknown_id}> does not exist."}}
