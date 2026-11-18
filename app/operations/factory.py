
from math import isfinite

from app.schemas.calculation import CalculationCreate, CalculationType


class CalculationFactory:
    """Perform calculations based on the selected operation."""

    @staticmethod
    def calculate(data: CalculationCreate) -> float:
        """Select and perform the correct calculation."""

        operations = {
            CalculationType.ADD: lambda a, b: a + b,
            CalculationType.SUBTRACT: lambda a, b: a - b,
            CalculationType.MULTIPLY: lambda a, b: a * b,
            CalculationType.DIVIDE: lambda a, b: a / b,
        }

        operation = operations[data.type]
        result = operation(data.a, data.b)

        if not isfinite(result):
            raise ValueError("Calculation result must be finite.")

        return result
