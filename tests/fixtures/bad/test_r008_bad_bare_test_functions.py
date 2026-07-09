"""Bad: test functions defined at module level instead of in classes."""


def test_addition():
    """Bad: bare module-level test function."""
    assert 1 + 1 == 2


def test_subtraction():
    """Bad: another bare module-level test function."""
    assert 5 - 3 == 2


def test_complex_operation():
    """Bad: yet another bare module-level test function."""
    result = [x for x in range(5)]
    assert len(result) == 5
