from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app
from tests.api.fixture_functions import create_unit_and_get_id, get_default_product


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_product(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)

    product = get_default_product(unit_id)
    response = client.post("/products", json=product)

    assert response.status_code == 201
    assert response.json() == {"product": {"id": ANY, **product}}


def test_should_not_create_product_that_exists(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)

    product = get_default_product(unit_id)
    client.post("/products", json=product)
    response = client.post("/products", json=product)

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "message": f"Product with barcode<{product['barcode']}> already exists."
        }
    }


def test_should_not_create_without_unit(client: TestClient) -> None:
    unknown_unit_id = str(uuid4())
    product = get_default_product(unknown_unit_id)
    response = client.post("/products", json=product)

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Unit with id<{unknown_unit_id}> does not exist."}
    }


def test_should_not_read_unknown_product(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Product with id<{unknown_id}> does not exist."}
    }


def test_should_persist_product(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)

    product = get_default_product(unit_id)
    response = client.post("/products", json=product)
    product_id = response.json()["product"]["id"]
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == {"product": {"id": product_id, **product}}


def test_get_all_products_on_empty(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": []}


def test_get_all_products(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)

    product = get_default_product(unit_id)
    response = client.post("/products", json=product)
    product_id = response.json()["product"]["id"]

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": [{"id": product_id, **product}]}


def test_update_product_price(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)

    product = get_default_product(unit_id, "Bread", "123456789", 10)
    response = client.post("/products", json=product)
    product_id = response.json()["product"]["id"]
    new_price = 20
    response = client.patch(f"/products/{product_id}/{new_price}")

    assert response.status_code == 200
    assert response.json() == {}

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == {
        "product": {"id": product_id, **product, "price": new_price}
    }


def test_should_not_update_unknown_product(client: TestClient) -> None:
    unknown_id = uuid4()
    new_price = 20
    response = client.patch(f"/products/{unknown_id}/{new_price}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Product with id<{unknown_id}> does not exist."}
    }
