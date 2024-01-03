from fastapi import APIRouter
from pydantic import BaseModel

from core.receipt import Sales
from infra.fastapi.dependables import ReceiptRepositoryDependable

sales_api = APIRouter(tags=["Sales"])


class SalesItem(BaseModel):
    n_receipts: int
    revenue: float


class SalesItemEnvelope(BaseModel):
    sales: SalesItem


@sales_api.get("/sales", status_code=200, response_model=SalesItemEnvelope)
def read_sales(receipts: ReceiptRepositoryDependable) -> dict[str, Sales]:
    return {"sales": receipts.read_sales()}
