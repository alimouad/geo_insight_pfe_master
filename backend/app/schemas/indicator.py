import enum

from datetime import datetime

from pydantic import BaseModel


class IndicatorCategory(str, enum.Enum):
    VEGETATION = "Vegetation"
    WATER = "Water"
    TEMPERATURE = "Temperature"
    CLIMATE = "Climate"
    LAND_COVER = "Land Cover"
    URBAN = "Urban"
    POPULATION = "Population"
    DEGRADATION = "Land Degradation"
    RISK = "Risk"


class IndicatorBase(BaseModel):
    category: IndicatorCategory
    name: str
    description: str | None = None
    formula: str | None = None
    unit: str | None = None
    color: str | None = None
    icon: str | None = None
    supported_dataset: str | None = None
    default_resolution: str | None = None
    color_palette: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    documentation: str | None = None
    applications: str | None = None
    is_active: bool = True


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorResponse(IndicatorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
