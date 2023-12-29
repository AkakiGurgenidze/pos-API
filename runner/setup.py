import os

from fastapi import FastAPI

from infra.fastapi.products import product_api
from infra.fastapi.receipts import receipt_api
from infra.fastapi.units import unit_api
from infra.in_memory.products import ProductsInMemory
from infra.in_memory.receipts import ReceiptsInMemory
from infra.in_memory.units import UnitsInMemory


def init_app():
    app = FastAPI()
    app.include_router(unit_api)
    app.include_router(product_api)
    app.include_router(receipt_api)

    if os.getenv("BOOK_REPOSITORY_KIND", "memory") == "sqlite":
        app.state.books = ...  # type: ignore
    else:
        app.state.units = UnitsInMemory()  # type: ignore
        app.state.products = ProductsInMemory(app.state.units)  # type: ignore
        app.state.receipts = ReceiptsInMemory(app.state.products)  # type: ignore

    return app
