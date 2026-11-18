
from enum import Enum
from math import isfinite

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class CalculationType(str, Enum):
    """Supported calculator operations."""

    ADD = "Add"
    SUBTRACT = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationCreate(BaseModel):
    """Validate data for a new calculation."""

    a: float
    b: float
    type: CalculationType

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value):
        if not isfinite(value):
            raise ValueError("Numbers must be finite.")
        return value

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self


class CalculationRead(BaseModel):
    """Define the data returned for a calculation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    a: float
    b: float
    type: CalculationType
    result: float
