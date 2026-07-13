"""
Advanced test examples demonstrating best practices.

Patterns shown:
- Fixtures with teardown
- Parametrized tests
- Mocking external calls
- Exception testing
- Async test support
"""

import pytest
from unittest.mock import Mock, patch
from src.example import Calculator, greet


# ---- Fixtures ----

@pytest.fixture
def calc() -> Calculator:
    """Provide a fresh Calculator for each test."""
    return Calculator()


@pytest.fixture
def populated_calc(calc: Calculator) -> Calculator:
    """A Calculator with some history."""
    calc.add(10, 5)
    calc.subtract(20, 3)
    return calc


# ---- Basic tests ----

class TestGreet:
    @pytest.mark.parametrize("name,expected_start", [
        ("World", "Hello"),
        ("Alice", "Hello"),
        ("", "Hello"),
        ("Jean-Pierre", "Hello"),
    ])
    def test_greet_format(self, name: str, expected_start: str) -> None:
        result = greet(name)
        assert result.startswith(expected_start)

    def test_greet_contains_name(self) -> None:
        assert "テスト" in greet("テスト")


# ---- Calculator edge cases ----

class TestCalculatorEdgeCases:
    def test_add_negative(self, calc: Calculator) -> None:
        assert calc.add(-5, -3) == -8

    def test_add_floats(self, calc: Calculator) -> None:
        assert calc.add(0.1, 0.2) == pytest.approx(0.3)

    def test_subtract_negative_result(self, calc: Calculator) -> None:
        assert calc.subtract(3, 10) == -7

    def test_multiply_by_zero(self, calc: Calculator) -> None:
        assert calc.multiply(5, 0) == 0

    def test_multiply_large_numbers(self, calc: Calculator) -> None:
        assert calc.multiply(10**6, 10**6) == 10**12

    def test_divide_by_zero_raises(self, calc: Calculator) -> None:
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)

    def test_divide_floor(self, calc: Calculator) -> None:
        assert calc.divide(7, 2) == 3.5

    def test_divide_negative(self, calc: Calculator) -> None:
        assert calc.divide(-10, 2) == -5

    def test_divide_by_one(self, calc: Calculator) -> None:
        assert calc.divide(42, 1) == 42


# ---- History tests ----

class TestHistory:
    def test_history_starts_empty(self, calc: Calculator) -> None:
        assert len(calc.history) == 0

    def test_history_tracks_operations(self, populated_calc: Calculator) -> None:
        assert len(populated_calc.history) == 2
        assert populated_calc.history[0][0] == "add"

    def test_clear_history(self, populated_calc: Calculator) -> None:
        populated_calc.clear_history()
        assert len(populated_calc.history) == 0

    def test_history_records_correct_results(self, calc: Calculator) -> None:
        calc.add(3, 7)
        calc.subtract(10, 4)
        assert calc.history[0][1] == 10
        assert calc.history[1][1] == 6


# ---- Mocking ----

class TestExternalMocking:
    def test_mock_Calculator(self) -> None:
        mock = Mock(spec=Calculator)
        mock.add.return_value = 99
        assert mock.add(1, 2) == 99
        mock.add.assert_called_once_with(1, 2)

    @patch("builtins.print")
    def test_calculator_runs_without_error(self, mock_print: Mock) -> None:
        """Verify the if __name__ block runs without exception."""
        from src.example import Calculator
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_multiple_operations_history_length(self) -> None:
        calc = Calculator()
        operations = [
            (calc.add, (1, 1)),
            (calc.subtract, (5, 2)),
            (calc.multiply, (3, 3)),
            (calc.divide, (10, 2)),
        ]
        for op, args in operations:
            op(*args)
        assert len(calc.history) == 4


# ---- Error path tests ----

class TestErrorPaths:
    def test_invalid_greet_type(self) -> None:
        with pytest.raises(TypeError):
            greet(123)  # type: ignore[arg-type]

    def test_calculator_chain_after_error(self, calc: Calculator) -> None:
        """Calculator should still work after an error."""
        with pytest.raises(ValueError):
            calc.divide(1, 0)
        assert calc.add(1, 2) == 3  # Still functional
