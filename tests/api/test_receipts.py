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


def create_unit_and_get_id(client):
    unit = {
        "name": "კგ"
    }
    response = client.post("/units", json=unit)
    unit_id = response.json()["unit"]["id"]
    return unit_id


def create_product_and_get_id(client, unit_id: UUID, product_price: int):
    product = get_product(unit_id, price=product_price)
    response = client.post("/products", json=product)
    product_id = response.json()["product"]["id"]
    return product_id


def test_should_create_receipt(client: TestClient) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert response.json() == {"receipt": {"id": ANY, "status": "open", "products": [], "total": 0}}


def test_should_add_product_in_receipt(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)
    product_price = 10
    product_id = create_product_and_get_id(client, unit_id, product_price)

    response = client.post("/receipts")
    receipt_id = response.json()['receipt']['id']
    response = client.post(f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3})

    assert response.status_code == 201
    assert response.json() == {"receipt": {"id": receipt_id,
                                           "status": "open",
                                           "products": [{
                                               "id": product_id,
                                               "quantity": 3,
                                               "price": 10,
                                               "total": 30
                                           }],
                                           "total": 30
                                           }
                               }


def test_read_by_id(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)
    product_price = 10
    product_id = create_product_and_get_id(client, unit_id, product_price)

    response = client.post("/receipts")
    receipt_id = response.json()['receipt']['id']
    client.post(f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3})

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json() == {"receipt": {"id": receipt_id,
                                           "status": "open",
                                           "products": [{
                                               "id": product_id,
                                               "quantity": 3,
                                               "price": 10,
                                               "total": 30
                                           }],
                                           "total": 30
                                           }
                               }


def test_should_not_read_unknown(client: TestClient) -> None:
    receipt_id = uuid4()

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 404
    assert response.json() == {"error": {"message": f"Receipt with id<{receipt_id}> does not exist."}}

#
# def test_should_not_create_product_that_exists(client: TestClient) -> None:
#     unit_id = get_unit_id(client)
#
#     product = get_product(unit_id)
#     client.post("/products", json=product)
#     response = client.post("/products", json=product)
#
#     assert response.status_code == 409
#     assert response.json() == {"error": {"message": f"Product with barcode<{product['barcode']}> already exists."}}
#
#
# # def test_should_not_create_without_unit(client: TestClient) -> None:
# #     product = get_product(uuid4())
# #     client.post("/products", json=product)
# #     response = client.post("/products", json=product)
# #
# #     assert response.status_code == 409
# #     assert response.json() == {"error": {"message": f"Product with barcode<{product['barcode']}> already exists."}}
#
#
# def test_should_not_read_unknown_product(client: TestClient) -> None:
#     unknown_id = uuid4()
#
#     response = client.get(f"/products/{unknown_id}")
#
#     assert response.status_code == 404
#     assert response.json() == {"error": {"message": f"Product with id<{unknown_id}> does not exist."}}
#
#
# def test_should_persist_product(client: TestClient):
#     unit_id = get_unit_id(client)
#
#     product = get_product(unit_id)
#     response = client.post("/products", json=product)
#     product_id = response.json()['product']['id']
#     response = client.get(f"/products/{product_id}")
#
#     assert response.status_code == 200
#     assert response.json() == {"product": {"id": product_id, **product}}
#
#
# def test_get_all_products_on_empty(client: TestClient):
#     response = client.get("/products")
#
#     assert response.status_code == 200
#     assert response.json() == {"products": []}
#
#
# def test_get_all_products(client: TestClient):
#     unit_id = get_unit_id(client)
#
#     product = get_product(unit_id)
#     response = client.post("/products", json=product)
#     product_id = response.json()['product']['id']
#
#     response = client.get("/products")
#
#     assert response.status_code == 200
#     assert response.json() == {"products": [{"id": product_id, **product}]}
#
#
# def test_update_product_price(client: TestClient):
#     unit_id = get_unit_id(client)
#
#     product = get_product(unit_id, "Bread", '123456789', 10)
#     response = client.post("/products", json=product)
#     product_id = response.json()['product']['id']
#     new_price = 20
#     response = client.patch(f'/products/{product_id}/{new_price}')
#
#     assert response.status_code == 200
#     assert response.json() == {}
#
#     response = client.get(f"/products/{product_id}")
#
#     assert response.status_code == 200
#     assert response.json() == {"product": {"id": product_id, **product, "price": new_price}}
#
#
# def test_should_not_update_unknown_product(client: TestClient):
#     unknown_id = uuid4()
#     new_price = 20
#     response = client.patch(f'/products/{unknown_id}/{new_price}')
#
#     assert response.status_code == 404
#     assert response.json() == {"error": {"message": f"Product with id<{unknown_id}> does not exist."}}
