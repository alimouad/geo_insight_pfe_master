from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.database import get_db
from app.models.indicator import Indicator, IndicatorCategory
from app.models.user import User
from app.schemas.indicator import IndicatorResponse

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
