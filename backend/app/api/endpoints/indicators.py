from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_admin, get_current_user
from app.database import get_db
from app.models.indicator import Indicator, IndicatorCategory
from app.models.user import User
from app.schemas.indicator import IndicatorCreate, IndicatorResponse, IndicatorUpdate

router = APIRouter()


@router.get("", response_model=list[IndicatorResponse])
def list_indicators(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Indicator).filter(Indicator.is_active.is_(True)).order_by(Indicator.name).all()


@router.get("/category/{category}", response_model=list[IndicatorResponse])
def list_indicators_by_category(category: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        category_enum = IndicatorCategory(category)
    except ValueError:
        raise HTTPException(status_code=404, detail="Unknown indicator category.")

    return (
        db.query(Indicator)
        .filter(Indicator.is_active.is_(True), Indicator.category == category_enum)
        .order_by(Indicator.name)
        .all()
    )


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(indicator_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found.")
    return indicator


@router.post("", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(
    payload: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    if db.query(Indicator).filter(Indicator.name == payload.name).first():
        raise HTTPException(status_code=400, detail="An indicator with this name already exists.")

    indicator = Indicator(**payload.model_dump())
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.put("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator(
    indicator_id: int,
    payload: IndicatorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if indicator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(indicator, field, value)

    db.commit()
    db.refresh(indicator)
    return indicator


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(indicator_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if indicator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

    db.delete(indicator)
    db.commit()
