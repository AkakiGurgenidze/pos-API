from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class Product:
    unit_id: UUID
    name: str
    barcode: str
    price: int
    id: UUID = field(default_factory=uuid4)


class ProductRepository(Protocol):
    def create(self, product: Product) -> None:
        pass

    def read(self, product_id: UUID) -> Product:
        pass

    def read_all(self) -> list[Product]:
        pass

    def update_price(self, product_id: UUID, new_price: int) -> None:
        pass
