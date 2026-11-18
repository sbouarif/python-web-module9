
import pytest
from pydantic import ValidationError

from app.schemas.calculation import CalculationCreate, CalculationRead
from app.operations.factory import CalculationFactory


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("Add", 10, 5, 15),
        ("Sub", 10, 5, 5),
        ("Multiply", 10, 5, 50),
        ("Divide", 10, 5, 2),
        ("Add", -5, 3, -2),
        ("Multiply", 2.5, 4, 10),
        ("Divide", 0, 5, 0),
    ],
)
def test_calculation_operations(operation, a, b, expected):
    """Check that each calculation returns the correct result."""
    data = CalculationCreate(a=a, b=b, type=operation)
    assert CalculationFactory.calculate(data) == pytest.approx(expected)


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"a": 10, "b": 0, "type": "Divide"},
        {"a": 10, "b": 5, "type": "Power"},
        {"a": "hello", "b": 5, "type": "Add"},
        {"a": 10, "b": 5, "type": "addition"},
        {"a": float("inf"), "b": 5, "type": "Add"},
        {"a": float("nan"), "b": 5, "type": "Multiply"},
    ],
)
def test_invalid_calculation_inputs(invalid_data):
    """Check that invalid calculation inputs are rejected."""
    with pytest.raises(ValidationError):
        CalculationCreate(**invalid_data)


def test_calculation_read():
    """Check that calculation output contains the correct fields."""
    data = CalculationRead(
        id=1,
        a=10,
        b=5,
        type="Add",
        result=15,
    )

    assert data.id == 1
    assert data.result == 15
    assert data.model_dump(mode="json")["type"] == "Add"


def test_calculation_overflow():
    """Check that an overflowing calculation is rejected."""
    data = CalculationCreate(a=1e308, b=1e308, type="Multiply")

    with pytest.raises(ValueError, match="finite"):
        CalculationFactory.calculate(data)
