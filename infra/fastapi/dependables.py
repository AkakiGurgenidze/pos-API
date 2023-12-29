from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from core.product import ProductRepository
from core.unit import UnitRepository


def get_unit_repository(request: Request) -> UnitRepository:
    return request.app.state.units  # type: ignore


UnitRepositoryDependable = Annotated[UnitRepository, Depends(get_unit_repository)]


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.products  # type: ignore


ProductRepositoryDependable = Annotated[ProductRepository, Depends(get_product_repository)]
