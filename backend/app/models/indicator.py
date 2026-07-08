import enum

from sqlalchemy.orm import relationship

from app.database import Base

from sqlalchemy import Column, Float, Integer, String, Text, Boolean, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

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


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)

    category = Column(SAEnum(IndicatorCategory), nullable=False)

    name = Column(String(255), nullable=False, unique=True)

    description = Column(Text)

    formula = Column(Text)

    unit = Column(String(50))

    # اللون الافتراضي فالواجهة
    color = Column(String(20))

    icon = Column(String(255))
    supported_dataset = Column(String(255))
    default_resolution = Column(String(50))
    color_palette = Column(Text)
    min_value = Column(Float)
    max_value = Column(Float)
    documentation = Column(Text)
    applications = Column(Text)

    # واش المؤشر ظاهر للمستخدم
    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    analyses = relationship(
        "Analysis",
        back_populates="indicator"
    )