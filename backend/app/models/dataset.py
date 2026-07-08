import enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


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



class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, unique=True)

    provider = Column(SAEnum(DatasetProvider), nullable=False)

    # Google Earth Engine Collection ID
    gee_collection = Column(String(255), nullable=False, unique=True)

    description = Column(Text)

    resolution = Column(String(120))

    # Vegetation, Climate, Elevation, Population...
    category = Column(SAEnum(DatasetCategory), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analyses = relationship("Analysis", back_populates="dataset")