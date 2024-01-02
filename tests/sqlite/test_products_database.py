import os
from uuid import uuid4

import pytest

from core.errors import AlreadyExistError, DoesNotExistError
from core.product import Product
from core.unit import Unit
from infra.sqlite.database_connect import Database
from infra.sqlite.products import ProductsDatabase
from infra.sqlite.units import UnitsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath("../infra/sqlite/start_up.sql"))
    db.initial()
    return db


def test_create_product(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    db.close_database()


def test_create_same_product_twice(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    with pytest.raises(AlreadyExistError):
        products.create(product)

    db.close_database()


def test_create_product_with_unknown_unit(db: Database) -> None:
    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(uuid4(), "Apple", "123456789", 10)

    with pytest.raises(DoesNotExistError):
        products.create(product)

    db.close_database()


def test_read_product(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    result_product = products.read(product.id)
    assert result_product == product

    db.close_database()


def test_read_unknown_product(db: Database) -> None:
    products = ProductsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        products.read(uuid4())


def test_read_all_product(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    assert products.read_all() == [product]

    db.close_database()


def test_update_product_price(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    products = ProductsDatabase(db.get_connection(), db.get_cursor())
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    products.update_price(product.id, 20)

    result_product = products.read(product.id)
    assert result_product.price == 20

    db.close_database()


def test_update_unknown_product_price(db: Database) -> None:
    UnitsDatabase(db.get_connection(), db.get_cursor())
    products = ProductsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        products.update_price(uuid4(), 20)

    db.close_database()
