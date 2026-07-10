def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


class Calculator:
    """A simple calculator class."""

    def __init__(self) -> None:
        self.history: list[tuple[str, float]] = []

    def add(self, x: float, y: float) -> float:
        result = x + y
        self.history.append(("add", result))
        return result

    def subtract(self, x: float, y: float) -> float:
        result = x - y
        self.history.append(("subtract", result))
        return result

    def multiply(self, x: float, y: float) -> float:
        result = x * y
        self.history.append(("multiply", result))
        return result

    def divide(self, x: float, y: float) -> float:
        if y == 0:
            raise ValueError("Cannot divide by zero")
        result = x / y
        self.history.append(("divide", result))
        return result

    def clear_history(self) -> None:
        self.history.clear()


if __name__ == "__main__":
    calc = Calculator()
    print(greet("World"))
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"History: {calc.history}")
