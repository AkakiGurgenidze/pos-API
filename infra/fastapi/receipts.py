from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from core.errors import AlreadyExistError, DoesNotExistError, ClosedReceiptError
from core.receipt import Receipt
from infra.fastapi.dependables import ReceiptRepositoryDependable

receipt_api = APIRouter(tags=["Receipts"])


class AddProductItem(BaseModel):
    id: UUID
    quantity: int


class ProductInReceiptItem(BaseModel):
    id: UUID
    quantity: int
    price: int
    total: int


class ReceiptItem(BaseModel):
    id: UUID
    status: str
    products: list[ProductInReceiptItem]
    total: int


class ReceiptItemEnvelope(BaseModel):
    receipt: ReceiptItem


class UpdateReceiptStatusItem(BaseModel):
    status: str


class EmptyResponse(BaseModel):
    pass


@receipt_api.post("/receipts",
                  status_code=201,
                  response_model=ReceiptItemEnvelope)
def create_product(receipts: ReceiptRepositoryDependable):
    receipt = Receipt()
    try:
        receipts.create(receipt)
        return {"receipt": receipt}
    except AlreadyExistError as e:
        return e.get_error_json_response(409)


@receipt_api.post("/receipts/{receipt_id}/products",
                  status_code=201,
                  response_model=ReceiptItemEnvelope)
def add_product(receipt_id: UUID, req: AddProductItem, receipts: ReceiptRepositoryDependable):
    try:
        return {"receipt": receipts.add_product(receipt_id, req.id, req.quantity)}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@receipt_api.get("/receipts/{receipt_id}",
                 status_code=200,
                 response_model=ReceiptItemEnvelope)
def read_by_id(receipt_id: UUID, receipts: ReceiptRepositoryDependable):
    try:
        return {"receipt": receipts.read(receipt_id)}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@receipt_api.patch("/receipts/{receipt_id}",
                   status_code=200,
                   response_model=EmptyResponse)
def read_by_id(receipt_id: UUID, req: UpdateReceiptStatusItem, receipts: ReceiptRepositoryDependable):
    try:
        receipts.update_status(receipt_id, req.status)
        return {}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@receipt_api.delete("/receipts/{receipt_id}",
                    status_code=200,
                    response_model=EmptyResponse)
def read_by_id(receipt_id: UUID, receipts: ReceiptRepositoryDependable):
    try:
        receipts.delete(receipt_id)
        return {}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)
    except ClosedReceiptError as e:
        return e.get_error_json_response(403)
