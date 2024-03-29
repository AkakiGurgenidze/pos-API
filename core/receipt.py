from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class ProductInReceipt:
    id: UUID
    quantity: int
    price: float
    total: float


@dataclass
class Receipt:
    status: str = "open"
    total: float = 0
    products: list[ProductInReceipt] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)


@dataclass
class Sales:
    n_receipts: int = 0
    revenue: float = 0


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> None:
        pass

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> Receipt:
        pass

    def read(self, receipt_id: UUID) -> Receipt:
        pass

    def update_status(self, receipt_id: UUID, new_status: str) -> None:
        pass

    def delete(self, receipt_id: UUID) -> None:
        pass

    def read_sales(self) -> Sales:
        pass
