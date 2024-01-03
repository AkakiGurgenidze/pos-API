from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app
from tests.api.fixture_functions import (
    create_product_and_get_id,
    create_unit_and_get_id,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_receipt(client: TestClient) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert response.json() == {
        "receipt": {"id": ANY, "status": "open", "products": [], "total": 0}
    }


def test_should_add_product_in_receipt(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)
    product_price = 1.5
    product_id = create_product_and_get_id(client, unit_id, product_price)

    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]
    response = client.post(
        f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3}
    )

    assert response.status_code == 201
    assert response.json() == {
        "receipt": {
            "id": receipt_id,
            "status": "open",
            "products": [{"id": product_id, "quantity": 3, "price": 1.5, "total": 4.5}],
            "total": 4.5,
        }
    }


def test_should_not_add_product_in_unknown_receipt(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)
    product_price = 10
    product_id = create_product_and_get_id(client, unit_id, product_price)

    receipt_id = uuid4()
    response = client.post(
        f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3}
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> does not exist."}
    }


def test_should_not_add_unknown_product_in_receipt(client: TestClient) -> None:
    product_id = str(uuid4())

    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]
    response = client.post(
        f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3}
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Product with id<{product_id}> does not exist."}
    }


def test_read_by_id(client: TestClient) -> None:
    unit_id = create_unit_and_get_id(client)
    product_price = 1.5
    product_id = create_product_and_get_id(client, unit_id, product_price)

    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]
    client.post(
        f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3}
    )

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json() == {
        "receipt": {
            "id": receipt_id,
            "status": "open",
            "products": [{"id": product_id, "quantity": 3, "price": 1.5, "total": 4.5}],
            "total": 4.5,
        }
    }


def test_should_not_read_unknown(client: TestClient) -> None:
    receipt_id = uuid4()

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> does not exist."}
    }


def test_should_change_status(client: TestClient) -> None:
    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]

    response = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    assert response.status_code == 200
    assert response.json() == {}

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json() == {
        "receipt": {"id": receipt_id, "status": "closed", "products": [], "total": 0}
    }


def test_should_not_change_status_on_unknown(client: TestClient) -> None:
    receipt_id = uuid4()
    response = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> does not exist."}
    }


def test_should_delete_receipt(client: TestClient) -> None:
    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]

    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 200
    assert response.json() == {}

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> does not exist."}
    }


def test_should_not_delete_closed_receipt(client: TestClient) -> None:
    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]
    client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})
    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 403
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> is closed."}
    }

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200


def test_should_not_delete_unknown_receipt(client: TestClient) -> None:
    receipt_id = uuid4()
    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> does not exist."}
    }
