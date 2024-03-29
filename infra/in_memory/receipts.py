from dataclasses import dataclass, field
from uuid import UUID

from core.errors import ClosedReceiptError, DoesNotExistError
from core.receipt import ProductInReceipt, Receipt, Sales
from infra.in_memory.products import ProductsInMemory


@dataclass
class ReceiptsInMemory:
    products: ProductsInMemory
    receipts: dict[UUID, Receipt] = field(default_factory=dict)

    def create(self, receipt: Receipt) -> None:
        self.receipts[receipt.id] = receipt

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> Receipt:
        product = self.products.read(product_id)
        try:
            self.receipts[receipt_id]
        except KeyError:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        self.receipts[receipt_id].products.append(
            ProductInReceipt(
                product_id, quantity, product.price, product.price * quantity
            )
        )
        self.receipts[receipt_id].total = product.price * quantity
        return self.receipts[receipt_id]

    def read(self, receipt_id: UUID) -> Receipt:
        try:
            return self.receipts[receipt_id]
        except KeyError:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

    def update_status(self, receipt_id: UUID, new_status: str) -> None:
        try:
            self.receipts[receipt_id]
        except KeyError:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        self.receipts[receipt_id].status = new_status

    def delete(self, receipt_id: UUID) -> None:
        try:
            self.receipts[receipt_id]
        except KeyError:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        if self.receipts[receipt_id].status == "closed":
            raise ClosedReceiptError("Receipt", "id", str(receipt_id))

        self.receipts.pop(receipt_id)

    def read_sales(self) -> Sales:
        n_receipts = 0
        revenue = 0.0

        for receipt in self.receipts.values():
            if receipt.status == "closed":
                n_receipts += 1
                revenue += receipt.total

        return Sales(n_receipts, revenue)
