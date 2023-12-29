from dataclasses import dataclass

from pydantic import BaseModel
from fastapi.responses import JSONResponse


class ErrorMessageResponse(BaseModel):
    message: str


class ErrorMessageEnvelope(BaseModel):
    error: ErrorMessageResponse


@dataclass
class AlreadyExistError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 409):
        return JSONResponse(
            status_code=code,
            content={"error": {"message": f"{self.name} with {self.field}<{self.value}> already exists."}}
        )


@dataclass
class DoesNotExistError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 404):
        return JSONResponse(
            status_code=code,
            content={"error": {"message": f"{self.name} with {self.field}<{self.value}> does not exist."}}
        )


@dataclass
class ClosedReceiptError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 403):
        return JSONResponse(
            status_code=code,
            content={"error": {"message": f"{self.name} with {self.field}<{self.value}> is closed."}}
        )

#
# class ErrorResponses:
#     @staticmethod
#     def get_already_exist_error_json(code: int, name: str, field: str, value: str):
#         return JSONResponse(
#             status_code=code,
#             content={"error": {"message": f"{name} with {field}<{value}> already exists."}}
#         )
#
#     @staticmethod
#     def get_doesnt_exist_error_json(code: int, name: str, field: str, value: str):
#         return JSONResponse(
#             status_code=code,
#             content={"error": {"message": f"{name} with {field}<{value}> does not exist."}}
#         )
#
#     @staticmethod
#     def get_closed_receipt_error_json(code: int, value: str):
#         return JSONResponse(
#             status_code=code,
#             content={"error": {"message": f"Receipt with id<{value}> is closed."}}
#         )
