from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.database import get_db
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import DatasetResponse

router = APIRouter()


@router.get("", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Dataset).filter(Dataset.is_active.is_(True)).order_by(Dataset.name).all()
