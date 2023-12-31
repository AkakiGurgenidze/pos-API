from infra.in_memory.sales import SalesInMemory


def test_read_sales() -> None:
    sales = SalesInMemory()

    assert sales.read().revenue == 0
    assert sales.read().n_receipts == 0


def test_update_sales() -> None:
    sales = SalesInMemory()

    sales.update(100)

    assert sales.read().revenue == 100
    assert sales.read().n_receipts == 1
