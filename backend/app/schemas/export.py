import enum

from datetime import datetime

from pydantic import BaseModel


class ExportType(str, enum.Enum):
    GEOTIFF = "GeoTIFF"
    PNG = "PNG"
    CSV = "CSV"
    GEOJSON = "GeoJSON"
    SHAPEFILE = "Shapefile"


class ExportBase(BaseModel):
    analysis_id: int
    type: ExportType
    file_url: str | None = None


class ExportCreate(BaseModel):
    analysis_id: int
    type: ExportType


class ExportResponse(ExportBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    file_name: str
    file_size: int | None
    mime_type: str | None
    status: str
    error_message: str | None = None
    download_count: int

    class Config:
        from_attributes = True
