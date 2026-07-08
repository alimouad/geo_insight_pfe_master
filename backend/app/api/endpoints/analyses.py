from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import from_shape, to_shape
from pydantic import BaseModel
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.core.gee_compute import NoImageryError, UnsupportedIndicatorError, compute_indicator
from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus
from app.models.dataset import Dataset
from app.models.indicator import Indicator
from app.models.project import Project
from app.models.user import User

router = APIRouter()


class AnalysisCreateRequest(BaseModel):
    project_id: int
    dataset_id: int
    indicator_id: int
    start_date: str
    end_date: str
    resolution: int
    cloud_percentage: float | None = None
    aoi: dict


def _to_multipolygon(geojson: dict):
    geom = shape(geojson)
    if isinstance(geom, Polygon):
        geom = MultiPolygon([geom])
    return geom


def _to_response(analysis: Analysis) -> dict:
    return {
        "id": analysis.id,
        "project_id": analysis.project_id,
        "user_id": analysis.user_id,
        "dataset_id": analysis.dataset_id,
        "indicator_id": analysis.indicator_id,
        "name": analysis.name,
        "description": analysis.description,
        "aoi": mapping(to_shape(analysis.aoi)),
        "start_date": analysis.start_date,
        "end_date": analysis.end_date,
        "status": analysis.status,
        "gee_task_id": analysis.gee_task_id,
        "gee_task_status": analysis.gee_task_status,
        "scale": analysis.scale,
        "cloud_percentage": analysis.cloud_percentage,
        "processing_time": analysis.processing_time,
        "result_path": analysis.result_path,
        "tile_url": analysis.tile_url,
        "stats": analysis.stats,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: AnalysisCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == payload.project_id, Project.user_id == current_user.id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found.")

    indicator = db.query(Indicator).filter(Indicator.id == payload.indicator_id).first()
    if indicator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

    try:
        geometry = _to_multipolygon(payload.aoi)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid AOI geometry.")

    started_at = datetime.now(timezone.utc)

    analysis = Analysis(
        project_id=project.id,
        user_id=current_user.id,
        dataset_id=dataset.id,
        indicator_id=indicator.id,
        name=f"{indicator.name} · {project.name}",
        aoi=from_shape(geometry, srid=4326),
        start_date=datetime.fromisoformat(payload.start_date),
        end_date=datetime.fromisoformat(payload.end_date),
        scale=payload.resolution,
        cloud_percentage=payload.cloud_percentage,
        status=AnalysisStatus.RUNNING,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        result = compute_indicator(
            provider=dataset.provider,
            gee_collection=dataset.gee_collection,
            indicator_name=indicator.name,
            aoi_geojson=payload.aoi,
            start_date=payload.start_date,
            end_date=payload.end_date,
            scale=payload.resolution,
            cloud_percentage=payload.cloud_percentage,
        )
        analysis.stats = {
            **result["stats"],
            "histogram": result["histogram"],
            "timeseries": result["timeseries"],
        }
        analysis.tile_url = result["tile_url"]
        analysis.result_path = result["png_url"]
        analysis.status = AnalysisStatus.COMPLETED
    except (UnsupportedIndicatorError, NoImageryError) as error:
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(error)
    except Exception as error:
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = f"Earth Engine computation failed: {error}"

    analysis.processing_time = (datetime.now(timezone.utc) - started_at).total_seconds()
    db.commit()
    db.refresh(analysis)

    return _to_response(analysis)


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return _to_response(analysis)


@router.get("")
def list_analyses(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    if project_id is not None:
        query = query.filter(Analysis.project_id == project_id)
    return [_to_response(a) for a in query.order_by(Analysis.created_at.desc()).all()]
