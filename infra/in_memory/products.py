from dataclasses import dataclass, field
from uuid import UUID

from core.errors import AlreadyExistError, DoesNotExistError
from core.product import Product
from infra.in_memory.units import UnitsInMemory


@dataclass
class ProductsInMemory:
    units: UnitsInMemory
    products: dict[UUID, Product] = field(default_factory=dict)

    def create(self, product: Product) -> None:
        self.units.read(product.unit_id)

        for curr_product in self.products.values():
            if curr_product.barcode == product.barcode:
                raise AlreadyExistError("Product", "barcode", product.barcode)
        self.products[product.id] = product

    def read(self, product_id: UUID) -> Product:
        try:
            return self.products[product_id]
        except KeyError:
            raise DoesNotExistError("Product", "id", str(product_id))

    def read_all(self) -> list[Product]:
        return list(self.products.values())

    def update_price(self, product_id: UUID, new_price: int) -> None:
        try:
            self.products[product_id]
        except KeyError:
            raise DoesNotExistError("Product", "id", str(product_id))

        self.products[product_id].price = new_price
