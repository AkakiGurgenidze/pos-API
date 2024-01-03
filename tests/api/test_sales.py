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


def test_should_be_zero_initially(client: TestClient) -> None:
    response = client.get("/sales")

    assert response.status_code == 200
    assert response.json() == {"sales": {"revenue": 0, "n_receipts": 0}}


def test_update_sales(client: TestClient) -> None:
    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]

    unit_id = create_unit_and_get_id(client)
    product_price = 1.5
    product_id = create_product_and_get_id(client, unit_id, product_price)
    client.post(
        f"/receipts/{receipt_id}/products", json={"id": product_id, "quantity": 3}
    )

    client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    response = client.get("/sales")

    assert response.status_code == 200
    assert response.json() == {"sales": {"revenue": 4.5, "n_receipts": 1}}
