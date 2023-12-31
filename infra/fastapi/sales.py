from fastapi import APIRouter
from pydantic import BaseModel

from infra.fastapi.dependables import SalesRepositoryDependable

sales_api = APIRouter(tags=["Sales"])


class SalesItem(BaseModel):
    n_receipts: int
    revenue: int


class SalesItemEnvelope(BaseModel):
    sales: SalesItem


@sales_api.get("/sales", status_code=200, response_model=SalesItemEnvelope)
def read_sales(sales: SalesRepositoryDependable):
    return {"sales": sales.read()}
