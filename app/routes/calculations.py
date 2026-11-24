from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.calculation import Calculation
from app.operations.factory import CalculationFactory
from app.schemas.calculation import (
    CalculationCreate,
    CalculationRead,
    CalculationUpdate,
)

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.id).all()


@router.get("/{calculation_id}", response_model=CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db)):
    calculation = db.get(Calculation, calculation_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@router.post("", response_model=CalculationRead, status_code=201)
def add_calculation(data: CalculationCreate, db: Session = Depends(get_db)):
    try:
        result = CalculationFactory.calculate(data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    calculation = Calculation(
        a=data.a, b=data.b, type=data.type.value, result=result
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


@router.put("/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    data: CalculationUpdate,
    db: Session = Depends(get_db),
):
    calculation = db.get(Calculation, calculation_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    try:
        result = CalculationFactory.calculate(data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    calculation.a = data.a
    calculation.b = data.b
    calculation.type = data.type.value
    calculation.result = result
    db.commit()
    db.refresh(calculation)
    return calculation


@router.delete("/{calculation_id}", status_code=204)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)):
    calculation = db.get(Calculation, calculation_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calculation)
    db.commit()
