import enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, func, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class ExportType(str, enum.Enum):
    GEOTIFF = "GeoTIFF"
    PNG = "PNG"
    CSV = "CSV"
    GEOJSON = "GeoJSON"
    SHAPEFILE = "Shapefile"

class Export(Base):
    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, index=True)

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type = Column(SAEnum(ExportType), nullable=False)

    file_name = Column(String(255), nullable=False)

    file_url = Column(String(1000), nullable=True)

    file_size = Column(BigInteger)

    mime_type = Column(String(100))

    status = Column(String(30), nullable=False, default="Processing")

    error_message = Column(String(500))

    download_count = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    analysis = relationship(
        "Analysis",
        back_populates="exports"
    )