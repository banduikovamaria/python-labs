class Calculator:
    """
    Проста ООП-програма для демонстрації unit-тестів.
    Має 3+ методи, які легко тестуються.
    """

    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b


if __name__ == "__main__":
    calc = Calculator()
    print("add:", calc.add(2, 3))
    print("subtract:", calc.subtract(10, 4))
    print("divide:", calc.divide(10, 2))
