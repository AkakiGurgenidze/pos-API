from dataclasses import dataclass, field
from sqlite3 import Connection, Cursor, IntegrityError, OperationalError
from uuid import UUID

from core.errors import ClosedReceiptError, DoesNotExistError
from core.receipt import ProductInReceipt, Receipt, Sales
from infra.in_memory.products import ProductsInMemory
from infra.sqlite.products import ProductsDatabase


@dataclass
class ReceiptsDatabase:
    con: Connection
    cur: Cursor

    def create(self, receipt: Receipt) -> None:
        self.cur.executemany(
            "insert into receipts(id, status) values (?,?)",
            [(str(receipt.id), receipt.status)],
        )
        self.con.commit()

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> Receipt:
        try:
            self.cur.executemany(
                "insert into products_in_receipts(receipt_id, product_id, quantity) values (?,?,?)",
                [(str(receipt_id), str(product_id), quantity)],
            )
        except IntegrityError as e:
            error_message = str(e)
            if "FOREIGN KEY constraint failed" in error_message:
                ProductsDatabase(self.con, self.cur).read(product_id)

        self.con.commit()

        return self.read(receipt_id)

    def read(self, receipt_id: UUID) -> Receipt:
        res_receipts = self.cur.execute(
            "select * from receipts where id = ?", [(str(receipt_id))]
        )
        result_receipts = res_receipts.fetchone()
        if result_receipts is None or result_receipts[0] is None:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        (
            receipt_id,
            status,
        ) = result_receipts

        receipt_total = 0
        products_in_receipts = []
        res_products_in_receipts = self.cur.execute(
            "select * from products_in_receipts where receipt_id = ?", [(str(receipt_id))]
        )
        for row in res_products_in_receipts.fetchall():
            (
                products_in_receipts_id,
                receipt_id,
                product_id,
                quantity
            ) = row
            product = ProductsDatabase(self.con, self.cur).read(product_id)
            total = product.price * quantity
            receipt_total += total
            products_in_receipts.append(ProductInReceipt(UUID(product_id), quantity, product.price, total))
        return Receipt(status, receipt_total, products_in_receipts, UUID(receipt_id))

    def update_status(self, receipt_id: UUID, new_status: str) -> None:
        self.cur.executemany(
            "update receipts set status=? where id = ?",
            [(new_status, str(receipt_id))],
        )
        if self.cur.rowcount <= 0:
            raise DoesNotExistError("Receipt", "id", str(receipt_id))

        self.con.commit()

    def delete(self, receipt_id: UUID) -> None:
        receipt = self.read(receipt_id)
        if receipt.status == "closed":
            raise ClosedReceiptError("Receipt", "id", str(receipt_id))
        self.cur.executemany(
            "delete from receipts where id = ?",
            [(str(receipt_id),)],
        )

        self.con.commit()

    def read_sales(self) -> Sales:
        n_receipts = 0
        revenue = 0

        res_receipts = self.cur.execute("select id from receipts where status = 'closed'")
        for row in res_receipts.fetchall():
            (
                receipt_id,
            ) = row

            n_receipts += 1

            res_products_in_receipts = self.cur.execute(
                "select * from products_in_receipts where receipt_id = ?", [(str(receipt_id))]
            )
            for row in res_products_in_receipts.fetchall():
                (
                    products_in_receipts_id,
                    receipt_id,
                    product_id,
                    quantity
                ) = row

                product = ProductsDatabase(self.con, self.cur).read(product_id)
                revenue += product.price * quantity

        return Sales(n_receipts, revenue)
