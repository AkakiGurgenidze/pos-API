import os

from fastapi import FastAPI

from infra.constants import DATABASE_NAME, SQL_FILE
from infra.fastapi.products import product_api
from infra.fastapi.receipts import receipt_api
from infra.fastapi.sales import sales_api
from infra.fastapi.units import unit_api
from infra.in_memory.products import ProductsInMemory
from infra.in_memory.receipts import ReceiptsInMemory
from infra.in_memory.units import UnitsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.products import ProductsDatabase
from infra.sqlite.receipts import ReceiptsDatabase
from infra.sqlite.units import UnitsDatabase


def init_app():
    app = FastAPI()
    app.include_router(unit_api)
    app.include_router(product_api)
    app.include_router(receipt_api)
    app.include_router(sales_api)

    if os.getenv("POS_REPOSITORY_KIND", "memory") == "sqlite":
        db = Database(DATABASE_NAME, os.path.abspath(SQL_FILE))
        # db.initial()    Uncomment this if you want to create initial db
        app.state.units = UnitsDatabase(db.get_connection(), db.get_cursor())  # type: ignore
        app.state.products = ProductsDatabase(db.get_connection(), db.get_cursor())  # type: ignore
        app.state.receipts = ReceiptsDatabase(db.get_connection(), db.get_cursor())  # type: ignore
    else:
        app.state.units = UnitsInMemory()  # type: ignore
        app.state.products = ProductsInMemory(app.state.units)  # type: ignore
        app.state.receipts = ReceiptsInMemory(app.state.products)  # type: ignore

    return app
