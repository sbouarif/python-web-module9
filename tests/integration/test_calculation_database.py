
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal, engine
from app.models.user import Base
from app.models.calculation import Calculation
from app.operations.factory import CalculationFactory
from app.schemas.calculation import CalculationCreate, CalculationRead


@pytest.fixture(scope="module", autouse=True)
def create_calculation_table():
    """Create the calculation table in PostgreSQL."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    """Use a transaction that rolls back after each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("Add", 10, 5, 15),
        ("Sub", 10, 5, 5),
        ("Multiply", 10, 5, 50),
        ("Divide", 10, 5, 2),
    ],
)
def test_save_calculation(db_session, operation, a, b, expected):
    """Verify calculations are stored correctly in PostgreSQL."""
    data = CalculationCreate(a=a, b=b, type=operation)
    result = CalculationFactory.calculate(data)

    calculation = Calculation(
        a=data.a,
        b=data.b,
        type=data.type.value,
        result=result,
    )

    db_session.add(calculation)
    db_session.flush()

    saved = db_session.execute(
        select(Calculation).where(Calculation.id == calculation.id)
    ).scalar_one()

    assert saved.a == a
    assert saved.b == b
    assert saved.type == operation
    assert saved.result == pytest.approx(expected)

    response = CalculationRead.model_validate(saved)
    assert response.result == pytest.approx(expected)


def test_database_rejects_missing_operand(db_session):
    """Verify PostgreSQL rejects a missing required operand."""
    calculation = Calculation(
        a=10,
        b=None,
        type="Add",
        result=10,
    )

    db_session.add(calculation)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_invalid_calculation_not_saved(db_session):
    """Verify invalid calculation data is rejected before insertion."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="Divide")

    assert db_session.query(Calculation).count() == 0
