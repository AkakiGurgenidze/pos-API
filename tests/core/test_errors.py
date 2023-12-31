from uuid import uuid4

from core.errors import AlreadyExistError, DoesNotExistError, ClosedReceiptError


def test_already_exist_error() -> None:
    json = AlreadyExistError("Unit", "name", "kg").get_error_json_response(409)
    assert json.status_code == 409
    assert json.body.decode('utf-8') == '{"error":{"message":"Unit with name<kg> already exists."}}'


def test_does_not_exist_error() -> None:
    unknown_id = uuid4()
    json = DoesNotExistError("Unit", "id", str(unknown_id)).get_error_json_response(404)
    assert json.status_code == 404
    assert json.body.decode('utf-8') == '{"error":{"message":"Unit with id<' + str(unknown_id) + '> does not exist."}}'


def test_closed_receipt_error() -> None:
    receipt_id = uuid4()
    json = ClosedReceiptError("Receipt", "id", str(receipt_id)).get_error_json_response(403)
    assert json.status_code == 403
    assert json.body.decode('utf-8') == '{"error":{"message":"Receipt with id<' + str(receipt_id) + '> is closed."}}'
