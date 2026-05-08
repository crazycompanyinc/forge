from app.legacy import calculate_invoice, find_duplicates


def test_calculate_invoice_basic():
    assert calculate_invoice([100, 200], 0.1, 10, "standard") == 320


def test_find_duplicates():
    assert find_duplicates(["a", "b", "a"]) == ["a"]
