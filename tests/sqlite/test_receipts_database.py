import os
from uuid import uuid4

import pytest

from core.errors import ClosedReceiptError, DoesNotExistError
from core.product import Product
from core.receipt import Receipt
from core.unit import Unit
from infra.constants import SQL_FILE_TEST
from infra.sqlite.database_connect import Database
from infra.sqlite.products import ProductsDatabase
from infra.sqlite.receipts import ReceiptsDatabase
from infra.sqlite.units import UnitsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_create_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)

    db.close_database()


def test_add_product_in_receipt(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

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

    db.close_database()


def test_add_unknown_product(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)

    with pytest.raises(DoesNotExistError):
        receipts.add_product(receipt.id, uuid4(), 10)

    db.close_database()


def test_add_product_unknown_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        receipts.add_product(uuid4(), uuid4(), 10)

    db.close_database()


def test_read_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)

    assert receipts.read(receipt.id) == receipt

    db.close_database()


def test_read_unknown_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        receipts.read(uuid4())

    db.close_database()


def test_update_status_of_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)
    receipts.update_status(receipt.id, "closed")

    assert receipts.read(receipt.id).status == "closed"

    db.close_database()


def test_delete_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)
    receipts.delete(receipt.id)

    with pytest.raises(DoesNotExistError):
        receipts.read(receipt.id)

    db.close_database()


def test_delete_unknown_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        receipts.delete(uuid4())

    db.close_database()


def test_delete_closed_receipt(db: Database) -> None:
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)
    receipts.update_status(receipt.id, "closed")

    with pytest.raises(ClosedReceiptError):
        receipts.delete(receipt.id)

    db.close_database()


def test_read_sales(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())

    receipt = Receipt()
    receipts.create(receipt)

    unit = Unit("kg")
    units.create(unit)

    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    result_receipt = receipts.add_product(receipt.id, product.id, 5)
    receipts.update_status(receipt.id, "closed")

    assert receipts.read_sales().n_receipts == 1
    assert receipts.read_sales().revenue == 50
