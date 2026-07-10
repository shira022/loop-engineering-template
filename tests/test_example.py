"""Tests for the example module."""

import pytest
from src.example import Calculator, greet


class TestGreet:
    def test_greet_returns_string(self):
        result = greet("World")
        assert isinstance(result, str)

    def test_greet_contains_name(self):
        result = greet("Alice")
        assert "Alice" in result


class TestCalculator:
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_subtract(self):
        calc = Calculator()
        assert calc.subtract(10, 4) == 6

    def test_multiply(self):
        calc = Calculator()
        assert calc.multiply(3, 4) == 12

    def test_divide(self):
        calc = Calculator()
        assert calc.divide(10, 2) == 5

    def test_divide_by_zero(self):
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)

    def test_history_tracks_operations(self):
        calc = Calculator()
        calc.add(1, 2)
        calc.subtract(5, 3)
        assert len(calc.history) == 2
        assert calc.history[0][0] == "add"

    def test_clear_history(self):
        calc = Calculator()
        calc.add(1, 1)
        calc.clear_history()
        assert len(calc.history) == 0
