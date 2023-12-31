from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from core.errors import ErrorMessageEnvelope, AlreadyExistError, DoesNotExistError
from core.product import Product
from infra.fastapi.dependables import ProductRepositoryDependable

product_api = APIRouter(tags=["Products"])


class CreateProductItem(BaseModel):
    unit_id: UUID
    name: str
    barcode: str
    price: int


class ProductItem(BaseModel):
    id: UUID
    unit_id: UUID
    name: str
    barcode: str
    price: int


class ProductItemEnvelope(BaseModel):
    product: ProductItem


class ProductListEnvelope(BaseModel):
    products: list[ProductItem]


class EmptyResponse(BaseModel):
    pass


@product_api.post(
    "/products",
    status_code=201,
    response_model=ProductItemEnvelope,
    responses={
        409: {"model": ErrorMessageEnvelope},
        404: {"model": ErrorMessageEnvelope},
    },
)
def create_product(request: CreateProductItem, products: ProductRepositoryDependable):
    print("aqweq")
    product = Product(**request.model_dump())
    print("zxcc")
    try:
        print("aqaaa")
        products.create(product)
        return {"product": product}
    except AlreadyExistError as e:
        return e.get_error_json_response(409)
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@product_api.get(
    "/products/{product_id}",
    status_code=200,
    response_model=ProductItemEnvelope,
    responses={404: {"model": ErrorMessageEnvelope}},
)
def read_product(product_id: UUID, products: ProductRepositoryDependable):
    try:
        return {"product": products.read(product_id)}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@product_api.get("/products", status_code=200, response_model=ProductListEnvelope)
def read_all_product(products: ProductRepositoryDependable):
    return {"products": products.read_all()}


@product_api.patch(
    "/products/{product_id}/{product_price}",
    status_code=200,
    response_model=EmptyResponse,
    responses={404: {"model": ErrorMessageEnvelope}},
)
def update_product(
    product_id: UUID, product_price: int, products: ProductRepositoryDependable
):
    try:
        products.update_price(product_id, product_price)
        return {}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)
