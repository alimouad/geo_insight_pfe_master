from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String(255), nullable=False, default="GeoInsight")
    version = Column(String(50), nullable=False, default="1.0.0")
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
