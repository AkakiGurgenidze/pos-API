from uuid import uuid4

import pytest

from core.errors import AlreadyExistError, DoesNotExistError, ClosedReceiptError
from core.product import Product
from core.receipt import Receipt
from core.unit import Unit
from infra.in_memory.products import ProductsInMemory
from infra.in_memory.receipts import ReceiptsInMemory
from infra.in_memory.units import UnitsInMemory


def test_create_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)


def test_add_product_in_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)

    unit = Unit("kg")
    units.create(unit)

    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    result_receipt = receipts.add_product(receipt.id, product.id, 5)

    assert result_receipt.products[0].id == product.id
    assert result_receipt.products[0].quantity == 5
    assert result_receipt.products[0].price == 10
    assert result_receipt.products[0].total == 50


def test_add_unknown_product_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)

    with pytest.raises(DoesNotExistError):
        receipts.add_product(receipt.id, uuid4(), 10)


def test_add_product_unknown_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    with pytest.raises(DoesNotExistError):
        receipts.add_product(uuid4(), uuid4(), 10)


def test_read_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)

    assert receipts.read(receipt.id) == receipt


def test_read_unknown_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    with pytest.raises(DoesNotExistError):
        receipts.read(uuid4())


def test_update_status_of_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)
    receipts.update_status(receipt.id, "closed")

    assert receipts.read(receipt.id).status == "closed"


def test_delete_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)
    receipts.delete(receipt.id)

    with pytest.raises(DoesNotExistError):
        receipts.read(receipt.id)


def test_delete_unknown_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    with pytest.raises(DoesNotExistError):
        receipts.delete(uuid4())


def test_delete_closed_receipt_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)
    receipts = ReceiptsInMemory(products)

    receipt = Receipt()
    receipts.create(receipt)
    receipts.update_status(receipt.id, "closed")

    with pytest.raises(ClosedReceiptError):
        receipts.delete(receipt.id)
