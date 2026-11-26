from calculator import safe_divide


def test_regular_division():
    assert safe_divide(8, 2) == 4


def test_zero_denominator_returns_none():
    assert safe_divide(8, 0) is None

