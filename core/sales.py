from dataclasses import dataclass
from typing import Protocol


@dataclass
class Sales:
    n_receipts: int = 0
    revenue: int = 0


class SalesRepository(Protocol):
    def update(self, plus_revenue_amount: int) -> None:
        pass

    def read(self) -> Sales:
        pass
