from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.endpoints.users import get_current_admin
from app.core.security import hash_password
from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus
from app.models.app_settings import AppSettings
from app.models.export import Export
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.project import ProjectResponse
from app.schemas.user import UserResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@router.get("/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_projects": db.query(Project).count(),
        "total_analyses": db.query(Analysis).count(),
        "total_exports": db.query(Export).count(),
        "running_tasks": db.query(Analysis).filter(Analysis.status == AnalysisStatus.RUNNING).count(),
        "failed_tasks": db.query(Analysis).filter(Analysis.status == AnalysisStatus.FAILED).count(),
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
