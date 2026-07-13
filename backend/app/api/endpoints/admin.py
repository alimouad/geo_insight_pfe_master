from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Area
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, EmailStr
from shapely.geometry import mapping
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from app.api.endpoints.analyses import execute_analysis
from app.api.endpoints.exports import EXTENSIONS, STORAGE_DIR, execute_export
from app.api.endpoints.users import get_current_admin
from app.core.activity_log import log_action
from app.core.security import hash_password
from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus
from app.models.app_settings import AppSettings
from app.models.dataset import Dataset
from app.models.export import Export
from app.models.indicator import Indicator
from app.models.project import Project
from app.models.system_log import SystemLog
from app.models.user import User, UserRole
from app.schemas.project import ProjectResponse
from app.schemas.user import UserResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@router.get("/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    total_coverage_m2 = db.query(func.coalesce(func.sum(ST_Area(cast(Analysis.aoi, Geography))), 0)).scalar()
    distinct_regions = db.query(Analysis.project_id).filter(Analysis.aoi.isnot(None)).distinct().count()

    return {
        "total_users": db.query(User).count(),
        "total_projects": db.query(Project).count(),
        "total_analyses": db.query(Analysis).count(),
        "total_exports": db.query(Export).count(),
        "running_tasks": db.query(Analysis).filter(Analysis.status == AnalysisStatus.RUNNING).count(),
        "failed_tasks": db.query(Analysis).filter(Analysis.status == AnalysisStatus.FAILED).count(),
        "total_coverage_km2": round(total_coverage_m2 / 1_000_000, 2),
        "distinct_regions": distinct_regions,
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class AdminUserCreateRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class AdminUserUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="This email is already registered.")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: AdminUserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.id == current_user.id and payload.role is not None and payload.role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="You cannot remove your own admin access.")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        user.email = payload.email
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Projects (all users)
# ---------------------------------------------------------------------------


@router.get("/projects", response_model=list[ProjectResponse])
def list_all_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


# ---------------------------------------------------------------------------
# Analysis Monitoring (all users)
# ---------------------------------------------------------------------------


def _analysis_to_admin_response(analysis: Analysis, owner: User | None, project: Project | None, indicator: Indicator | None) -> dict:
    return {
        "id": analysis.id,
        "name": analysis.name,
        "status": analysis.status,
        "owner": owner.full_name if owner else None,
        "owner_email": owner.email if owner else None,
        "project": project.name if project else None,
        "indicator": indicator.name if indicator else None,
        "scale": analysis.scale,
        "processing_time": analysis.processing_time,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at,
    }


@router.get("/analyses")
def list_all_analyses(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    results = []
    for analysis in analyses:
        owner = db.query(User).filter(User.id == analysis.user_id).first()
        project = db.query(Project).filter(Project.id == analysis.project_id).first()
        indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
        results.append(_analysis_to_admin_response(analysis, owner, project, indicator))
    return results


@router.post("/analyses/{analysis_id}/retry")
def retry_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    dataset = db.query(Dataset).filter(Dataset.id == analysis.dataset_id).first()
    indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
    if dataset is None or indicator is None:
        raise HTTPException(status_code=400, detail="The dataset or indicator for this analysis is no longer available.")

    analysis.status = AnalysisStatus.RUNNING
    analysis.error_message = None
    db.commit()
    db.refresh(analysis)

    aoi_geojson = mapping(to_shape(analysis.aoi))
    execute_analysis(analysis, dataset, indicator, aoi_geojson, db, log_user_id=current_user.id)

    owner = db.query(User).filter(User.id == analysis.user_id).first()
    project = db.query(Project).filter(Project.id == analysis.project_id).first()
    return _analysis_to_admin_response(analysis, owner, project, indicator)


@router.post("/analyses/{analysis_id}/cancel")
def cancel_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    if analysis.status != AnalysisStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Only running analyses can be cancelled.")

    analysis.status = AnalysisStatus.FAILED
    analysis.error_message = "Cancelled by administrator."
    db.commit()
    db.refresh(analysis)

    log_action(db, user_id=current_user.id, action="Analysis Cancelled", details=analysis.name)

    owner = db.query(User).filter(User.id == analysis.user_id).first()
    project = db.query(Project).filter(Project.id == analysis.project_id).first()
    indicator = db.query(Indicator).filter(Indicator.id == analysis.indicator_id).first()
    return _analysis_to_admin_response(analysis, owner, project, indicator)


@router.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    name = analysis.name
    db.delete(analysis)
    db.commit()

    log_action(db, user_id=current_user.id, action="Analysis Deleted", details=name)


# ---------------------------------------------------------------------------
# Export Monitoring (all users)
# ---------------------------------------------------------------------------


def _export_to_admin_response(export: Export, analysis: Analysis | None, owner: User | None) -> dict:
    return {
        "id": export.id,
        "file_name": export.file_name,
        "type": export.type,
        "status": export.status,
        "file_size": export.file_size,
        "download_count": export.download_count,
        "owner": owner.full_name if owner else None,
        "owner_email": owner.email if owner else None,
        "analysis": analysis.name if analysis else None,
        "error_message": export.error_message,
        "created_at": export.created_at,
    }


@router.get("/exports")
def list_all_exports(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    exports = db.query(Export).order_by(Export.created_at.desc()).all()
    results = []
    for export in exports:
        analysis = db.query(Analysis).filter(Analysis.id == export.analysis_id).first()
        owner = db.query(User).filter(User.id == analysis.user_id).first() if analysis else None
        results.append(_export_to_admin_response(export, analysis, owner))
    return results


@router.post("/exports/{export_id}/retry")
def retry_export(export_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    export = db.query(Export).filter(Export.id == export_id).first()
    if export is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found.")

    analysis = db.query(Analysis).filter(Analysis.id == export.analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=400, detail="The analysis for this export no longer exists.")

    export.status = "Processing"
    export.error_message = None
    db.commit()
    db.refresh(export)

    execute_export(export, analysis, db, log_user_id=current_user.id)

    owner = db.query(User).filter(User.id == analysis.user_id).first()
    return _export_to_admin_response(export, analysis, owner)


@router.delete("/exports/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_export_admin(export_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    export = db.query(Export).filter(Export.id == export_id).first()
    if export is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found.")

    extension = EXTENSIONS.get(export.type, "bin")
    disk_path = STORAGE_DIR / f"{export.id}.{extension}"
    disk_path.unlink(missing_ok=True)

    name = export.file_name
    db.delete(export)
    db.commit()

    log_action(db, user_id=current_user.id, action="Export Deleted", details=name)


# ---------------------------------------------------------------------------
# System Logs
# ---------------------------------------------------------------------------


@router.get("/logs")
def list_system_logs(
    action: str | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    query = db.query(SystemLog)
    if action is not None:
        query = query.filter(SystemLog.action == action)
    logs = query.order_by(SystemLog.created_at.desc()).limit(min(limit, 500)).all()

    results = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        results.append(
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "user": user.full_name if user else None,
                "user_email": user.email if user else None,
                "created_at": log.created_at,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class AppSettingsResponse(BaseModel):
    app_name: str
    version: str
    maintenance_mode: bool

    class Config:
        from_attributes = True


class AppSettingsUpdateRequest(BaseModel):
    app_name: str | None = None
    version: str | None = None
    maintenance_mode: bool | None = None


def _get_or_create_settings(db: Session) -> AppSettings:
    settings = db.query(AppSettings).first()
    if settings is None:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=AppSettingsResponse)
def get_app_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return _get_or_create_settings(db)


@router.put("/settings", response_model=AppSettingsResponse)
def update_app_settings(
    payload: AppSettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    settings = _get_or_create_settings(db)
    if payload.app_name is not None:
        settings.app_name = payload.app_name
    if payload.version is not None:
        settings.version = payload.version
    if payload.maintenance_mode is not None:
        settings.maintenance_mode = payload.maintenance_mode

    db.commit()
    db.refresh(settings)
    return settings
