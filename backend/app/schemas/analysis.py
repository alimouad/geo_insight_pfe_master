import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnalysisStatus(str, enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class AnalysisBase(BaseModel):
    project_id: int
    user_id: int
    dataset_id: int | None = None
    indicator_id: int | None = None
    name: str
    description: str | None = None
    aoi: Any
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    gee_task_id: str | None = None
    gee_task_status: str | None = None
    scale: int | None = None
    cloud_percentage: float | None = None
    processing_time: float | None = None
    result_path: str | None = None


class AnalysisCreate(AnalysisBase):
    pass


class AnalysisUpdate(BaseModel):
    dataset_id: int | None = None
    indicator_id: int | None = None
    name: str | None = None
    description: str | None = None
    aoi: Any | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: AnalysisStatus | None = None
    gee_task_id: str | None = None
    gee_task_status: str | None = None
    scale: int | None = None
    cloud_percentage: float | None = None
    processing_time: float | None = None
    result_path: str | None = None


class AnalysisResponse(AnalysisBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True