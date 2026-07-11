from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from geoalchemy2 import Geography
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_user
from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus
from app.models.dataset import Dataset
from app.models.export import Export
from app.models.indicator import Indicator
from app.models.project import Project
from app.models.user import User

router = APIRouter()


def _apply_filters(query, current_user, date_from, date_to, project_id, dataset_id, indicator_id):
    query = query.filter(Analysis.user_id == current_user.id)
    if date_from:
        query = query.filter(Analysis.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(Analysis.created_at <= datetime.fromisoformat(date_to))
    if project_id:
        query = query.filter(Analysis.project_id == project_id)
    if dataset_id:
        query = query.filter(Analysis.dataset_id == dataset_id)
    if indicator_id:
        query = query.filter(Analysis.indicator_id == indicator_id)
    return query


class Filters:
    def __init__(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        project_id: int | None = None,
        dataset_id: int | None = None,
        indicator_id: int | None = None,
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.indicator_id = indicator_id


@router.get("/overview")
def get_overview(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = _apply_filters(db.query(Analysis), current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id)

    total_analyses = base.count()
    completed = base.filter(Analysis.status == AnalysisStatus.COMPLETED).count()
    running = base.filter(Analysis.status == AnalysisStatus.RUNNING).count()
    failed = base.filter(Analysis.status == AnalysisStatus.FAILED).count()

    projects_query = db.query(Project).filter(Project.user_id == current_user.id)
    if filters.project_id:
        projects_query = projects_query.filter(Project.id == filters.project_id)
    total_projects = projects_query.count()

    exports_count = (
        db.query(Export)
        .join(Analysis, Export.analysis_id == Analysis.id)
        .filter(Analysis.user_id == current_user.id)
    )
    if filters.project_id:
        exports_count = exports_count.filter(Analysis.project_id == filters.project_id)
    exports_count = exports_count.count()

    area_m2 = (
        _apply_filters(
            db.query(func.coalesce(func.sum(func.ST_Area(cast(Analysis.aoi, Geography))), 0.0)),
            current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
        ).scalar()
    )
    total_area_ha = round((area_m2 or 0) / 10_000, 2)

    avg_processing_time = (
        _apply_filters(
            db.query(func.avg(Analysis.processing_time)).filter(Analysis.status == AnalysisStatus.COMPLETED),
            current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
        ).scalar()
    )

    return {
        "projects": total_projects,
        "analyses": total_analyses,
        "completed": completed,
        "running": running,
        "failed": failed,
        "exports": exports_count,
        "total_area_ha": total_area_ha,
        "avg_processing_time": round(avg_processing_time, 2) if avg_processing_time is not None else None,
    }


@router.get("/status")
def get_status_breakdown(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _apply_filters(
        db.query(Analysis.status, func.count(Analysis.id)).group_by(Analysis.status),
        current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
    )
    return [{"status": status, "count": count} for status, count in query.all()]


@router.get("/indicators")
def get_indicator_usage(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _apply_filters(
        db.query(Indicator.name, func.count(Analysis.id))
        .join(Analysis, Analysis.indicator_id == Indicator.id)
        .group_by(Indicator.name)
        .order_by(func.count(Analysis.id).desc()),
        current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
    )
    return [{"indicator": name, "count": count} for name, count in query.all()]


@router.get("/datasets")
def get_dataset_usage(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _apply_filters(
        db.query(Dataset.name, func.count(Analysis.id))
        .join(Analysis, Analysis.dataset_id == Dataset.id)
        .group_by(Dataset.name)
        .order_by(func.count(Analysis.id).desc()),
        current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
    )
    return [{"dataset": name, "count": count} for name, count in query.all()]


@router.get("/monthly")
def get_monthly_activity(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    month_bucket = func.to_char(Analysis.created_at, "YYYY-MM")
    query = _apply_filters(
        db.query(month_bucket.label("month"), func.count(Analysis.id)).group_by(month_bucket).order_by(month_bucket),
        current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
    )
    return [{"month": month, "count": count} for month, count in query.all()]


@router.get("/projects")
def get_project_activity(
    filters: Filters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _apply_filters(
        db.query(Project.name, func.count(Analysis.id))
        .join(Analysis, Analysis.project_id == Project.id)
        .group_by(Project.name)
        .order_by(func.count(Analysis.id).desc()),
        current_user, filters.date_from, filters.date_to, filters.project_id, filters.dataset_id, filters.indicator_id,
    ).limit(8)
    return [{"project": name, "count": count} for name, count in query.all()]
