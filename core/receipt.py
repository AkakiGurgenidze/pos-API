from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class ProductInReceipt:
    id: UUID
    quantity: int
    price: int
    total: int


@dataclass
class Receipt:
    status: str
    products: list[ProductInReceipt]

    id: UUID = field(default_factory=uuid4)


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> None:
        pass

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> None:
        pass

    def read(self, receipt_id: UUID) -> Receipt:
        pass

    def update_status(self, receipt_id: UUID, new_status: str) -> None:
        pass

    def delete(self, receipt_id: UUID) -> None:
        pass
