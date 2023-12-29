# from dataclasses import field, dataclass
# from typing import Any
# from uuid import uuid4
#
# import pytest
#
# from unittest.mock import ANY
#
# from faker import Faker
# from fastapi.testclient import TestClient
#
# from runner.setup import init_app
#
#
# @pytest.fixture
# def client() -> TestClient:
#     return TestClient(init_app())
#
#
# @dataclass
# class Fake:
#     faker: Faker = field(default_factory=Faker)
#
#     def book(self, author: str = "") -> dict[str, Any]:
#         return {
#             "name": self.faker.catch_phrase(),
#             "isbn": self.faker.isbn13(),
#             "author": author or self.faker.name(),
#         }
#
#
# def test_should_not_read_unknown(client: TestClient) -> None:
#     unknown_id = uuid4()
#
#     response = client.get(f"/books/{unknown_id}")
#
#     assert response.status_code == 404
#     assert response.json() == {"message": f"Book with id<{unknown_id}> does not exist."}
#
#
# def test_should_create(client: TestClient) -> None:
#     book = Fake().book()
#
#     response = client.post("/books", json=book)
#
#     assert response.status_code == 201
#     assert response.json() == {"book": {"id": ANY, **book}}
#
#
# def test_should_persist(client: TestClient):
#     book = Fake().book()
#
#     response = client.post("/books", json=book)
#     book_id = response.json()["book"]["id"]
#
#     response = client.get(f"/books/{book_id}")
#
#     assert response.status_code == 200
#     assert response.json() == {"id": book_id, **book}
#
#
# def test_get_all_books_on_empty(client: TestClient):
#     response = client.get("/books")
#
#     assert response.status_code == 200
#     assert response.json() == {"books": []}
#
#
# def test_get_all_books(client: TestClient):
#     book = Fake().book()
#
#     response = client.post("/books", json=book)
#     book_id = response.json()["book"]["id"]
#
#     response = client.get("/books")
#
#     assert response.status_code == 200
#     assert response.json() == {"books": [{"id": book_id, **book}]}
#
#
# def test_filtered_book_authors_starts_with_a(client: TestClient):
#     book1 = Fake().book(author="aranz Kafka")
#     book2 = Fake().book(author="branz Kafka")
#
#     response = client.post("/books", json=book1)
#     book1_id = response.json()["book"]["id"]
#     client.post("/books", json=book2)
#
#     response = client.get("/books?author_starts_with=a")
#
#     assert response.status_code == 200
#     assert response.json() == {"books": [{"id": book1_id, **book1}]}
