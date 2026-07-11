from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.database import get_db
from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.export import Export
from app.models.favorite import Favorite
from app.models.indicator import Indicator
from app.models.project import Project
from app.models.user import User

router = APIRouter()


class FavoriteCreateRequest(BaseModel):
    analysis_id: int


def _to_response(favorite: Favorite, db: Session) -> dict:
    analysis = favorite.analysis
    project = db.query(Project).filter(Project.id == analysis.project_id).first()
    dataset = db.query(Dataset).filter(Dataset.id == analysis.dataset_id).first()
    indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
    latest_export = (
        db.query(Export)
        .filter(Export.analysis_id == analysis.id, Export.status == "Completed")
        .order_by(Export.created_at.desc())
        .first()
    )

    return {
        "id": favorite.id,
        "analysis_id": analysis.id,
        "created_at": favorite.created_at,
        "project_id": analysis.project_id,
        "project_name": project.name if project else None,
        "indicator_name": indicator.name if indicator else analysis.name,
        "dataset_name": dataset.name if dataset else None,
        "analysis_status": analysis.status,
        "analysis_created_at": analysis.created_at,
        "export_id": latest_export.id if latest_export else None,
    }


@router.get("")
def list_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favorites = (
        db.query(Favorite)
        .join(Analysis, Favorite.analysis_id == Analysis.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return [_to_response(f, db) for f in favorites]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_favorite(
    payload: FavoriteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = db.query(Analysis).filter(Analysis.id == payload.analysis_id, Analysis.user_id == current_user.id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    existing = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.analysis_id == analysis.id).first()
    if existing is not None:
        return _to_response(existing, db)

    favorite = Favorite(user_id=current_user.id, analysis_id=analysis.id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return _to_response(favorite, db)


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(favorite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.user_id == current_user.id).first()
    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found.")
    db.delete(favorite)
    db.commit()


@router.delete("/by-analysis/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite_by_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favorite = db.query(Favorite).filter(Favorite.analysis_id == analysis_id, Favorite.user_id == current_user.id).first()
    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found.")
    db.delete(favorite)
    db.commit()
