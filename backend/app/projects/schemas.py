from pydantic import BaseModel

from app.schemas.project import ProjectStatus


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None
    geometry: dict | None = None
    area: float | None = None
    status: ProjectStatus | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    geometry: dict | None = None
    area: float | None = None
    status: ProjectStatus | None = None


class AoiPayload(BaseModel):
    geometry: dict
    area: float
