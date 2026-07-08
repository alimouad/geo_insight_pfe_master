from datetime import datetime
import enum

from pydantic import BaseModel


class ProjectStatus(str, enum.Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class ProjectBase(BaseModel):
    user_id: int
    name: str
    description: str | None = None
    geometry: str | None = None
    area: float | None = None
    status: ProjectStatus = ProjectStatus.RUNNING


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    geometry: str | None = None
    area: float | None = None
    status: ProjectStatus | None = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True