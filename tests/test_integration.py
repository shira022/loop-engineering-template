"""
Integration test examples.

These test the interaction between multiple components.
"""

from src.example import Calculator, greet


class TestGreetAndCalculate:
    """Test that greet and Calculator work together."""

    def test_greet_then_calculate(self) -> None:
        name = "World"
        message = greet(name)
        assert "World" in message

        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5
        assert len(calc.history) == 1

    def test_workflow(self) -> None:
        """Simulate a real usage workflow."""
        calc = Calculator()

        # User does several calculations
        results = [
            calc.add(5, 3),       # 8
            calc.multiply(2, 4),  # 8
            calc.subtract(10, 3), # 7
            calc.divide(9, 3),    # 3
        ]
        assert results == [8, 8, 7, 3]
        assert len(calc.history) == 4
