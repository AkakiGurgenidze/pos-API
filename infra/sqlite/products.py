from dataclasses import dataclass
from sqlite3 import Connection, Cursor, IntegrityError
from uuid import UUID

from core.errors import AlreadyExistError, DoesNotExistError
from core.product import Product


@dataclass
class ProductsDatabase:
    con: Connection
    cur: Cursor

    def create(self, product: Product) -> None:
        try:
            self.cur.executemany(
                "insert into products(id, unit_id, name, barcode, price) "
                "values (?,?,?,?,?)",
                [
                    (
                        str(product.id),
                        str(product.unit_id),
                        product.name,
                        product.barcode,
                        product.price,
                    )
                ],
            )
            self.con.commit()
        except IntegrityError as e:
            error_message = str(e)
            if "FOREIGN KEY constraint failed" in error_message:
                raise DoesNotExistError("Unit", "id", str(product.unit_id))
            elif (
                "UNIQUE constraint failed" in error_message
                and "barcode" in error_message
            ):
                raise AlreadyExistError("Product", "barcode", product.barcode)

    def read(self, product_id: UUID) -> Product:
        res = self.cur.execute("select * from products where id = ?", [str(product_id)])
        result = res.fetchone()
        if result is not None and result[0] is not None:
            (id, unit_id, name, barcode, price) = result
            return Product(UUID(unit_id), name, barcode, price, UUID(id))
        else:
            raise DoesNotExistError("Product", "id", str(product_id))

    def read_all(self) -> list[Product]:
        products = []
        res = self.cur.execute("select * from products")
        for row in res.fetchall():
            (id, unit_id, name, barcode, price) = row
            products.append(Product(UUID(unit_id), name, barcode, price, UUID(id)))
        return products

    def update_price(self, product_id: UUID, new_price: float) -> None:
        self.cur.executemany(
            "update products set price=? where id = ?",
            [(round(new_price, 2), str(product_id))],
        )
        if self.cur.rowcount <= 0:
            raise DoesNotExistError("Product", "id", str(product_id))

        self.con.commit()
