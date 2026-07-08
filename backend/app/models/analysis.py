import enum

from geoalchemy2 import Geometry
from sqlalchemy import JSON, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class AnalysisStatus(str, enum.Enum):
	PENDING = "Pending"
	RUNNING = "Running"
	COMPLETED = "Completed"
	FAILED = "Failed"


class Analysis(Base):
	__tablename__ = "analyses"

	id = Column(Integer, primary_key=True, index=True)
	project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
	indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="SET NULL"), nullable=True, index=True)
	name = Column(String(255), nullable=False)
	description = Column(Text, nullable=True)
	aoi = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
	start_date = Column(DateTime(timezone=True), nullable=True)
	end_date = Column(DateTime(timezone=True), nullable=True)
	status = Column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
	gee_task_id = Column(String(255), nullable=True)
	gee_task_status = Column(String(50), nullable=True)
	scale = Column(Integer, nullable=True)
	cloud_percentage = Column(Float, nullable=True)
	processing_time = Column(Float, nullable=True)
	result_path = Column(String(1000), nullable=True)
	tile_url = Column(String(1000), nullable=True)
	stats = Column(JSON, nullable=True)
	error_message = Column(Text, nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	project = relationship("Project", back_populates="analyses")
	user = relationship("User", back_populates="analyses")
	dataset = relationship("Dataset", back_populates="analyses")
	indicator = relationship("Indicator", back_populates="analyses")
	exports = relationship("Export", back_populates="analysis", cascade="all, delete-orphan")
	favorites = relationship("Favorite", back_populates="analysis", cascade="all, delete-orphan")
