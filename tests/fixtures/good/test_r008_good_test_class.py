"""Good: test functions properly organized in classes."""


class TestBasicFunctionality:
    """Test group for basic functionality."""

    def test_addition(self):
        """Test basic addition."""
        assert 1 + 1 == 2

    def test_subtraction(self):
        """Test basic subtraction."""
        assert 5 - 3 == 2


class TestAdvancedFunctionality:
    """Test group for advanced functionality."""

    def test_complex_logic(self):
        """Test complex logic."""
        result = [x for x in range(5)]
        assert len(result) == 5
