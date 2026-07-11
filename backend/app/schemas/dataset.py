import enum

from datetime import datetime

from pydantic import BaseModel


class DatasetProvider(str, enum.Enum):
    SENTINEL_2 = "Sentinel-2"
    LANDSAT_8 = "Landsat-8"
    MODIS = "MODIS"
    CHIRPS = "CHIRPS"
    WORLDPOP = "WorldPop"


class DatasetCategory(str, enum.Enum):
    VEGETATION = "Vegetation"
    CLIMATE = "Climate"
    ELEVATION = "Elevation"
    POPULATION = "Population"
    LAND_COVER = "Land Cover"
    WATER = "Water"
    URBAN = "Urban"


class DatasetBase(BaseModel):
    name: str
    provider: DatasetProvider
    gee_collection: str
    description: str | None = None
    resolution: str | None = None
    category: DatasetCategory
    is_active: bool = True


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: str | None = None
    provider: DatasetProvider | None = None
    gee_collection: str | None = None
    description: str | None = None
    resolution: str | None = None
    category: DatasetCategory | None = None
    is_active: bool | None = None


class DatasetResponse(DatasetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True