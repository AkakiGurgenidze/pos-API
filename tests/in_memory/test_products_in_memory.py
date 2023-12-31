from uuid import uuid4

import pytest

from core.errors import AlreadyExistError, DoesNotExistError
from core.product import Product
from core.unit import Unit
from infra.in_memory.products import ProductsInMemory
from infra.in_memory.units import UnitsInMemory


def test_create_product_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    products = ProductsInMemory(units)
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)


def test_create_same_product_twice_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    products = ProductsInMemory(units)
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    with pytest.raises(AlreadyExistError):
        products.create(product)


def test_create_product_with_unknown_unit_in_memory() -> None:
    units = UnitsInMemory()

    products = ProductsInMemory(units)
    product = Product(uuid4(), "Apple", "123456789", 10)

    with pytest.raises(DoesNotExistError):
        products.create(product)


def test_read_product_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    products = ProductsInMemory(units)
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    result_product = products.read(product.id)
    assert result_product == product


def test_read_unknown_product_in_memory() -> None:
    units = UnitsInMemory()

    products = ProductsInMemory(units)

    with pytest.raises(DoesNotExistError):
        products.read(uuid4())


def test_read_all_product_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    products = ProductsInMemory(units)
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    assert products.read_all() == [product]


def test_update_product_price_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    products = ProductsInMemory(units)
    product = Product(unit.id, "Apple", "123456789", 10)
    products.create(product)

    products.update_price(product.id, 20)

    result_product = products.read(product.id)
    assert result_product.price == 20


def test_update_unknown_product_price_in_memory() -> None:
    units = UnitsInMemory()
    products = ProductsInMemory(units)

    with pytest.raises(DoesNotExistError):
        products.update_price(uuid4(), 20)
