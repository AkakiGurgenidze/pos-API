from dataclasses import dataclass, field

from core.sales import Sales


@dataclass
class SalesInMemory:
    sales: Sales = field(default_factory=Sales)

    def update(self, plus_revenue_amount: int) -> None:
        self.sales.n_receipts += 1
        self.sales.revenue += plus_revenue_amount

    def read(self) -> Sales:
        return self.sales
