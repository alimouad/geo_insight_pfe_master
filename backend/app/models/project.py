import enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class ProjectStatus(str, enum.Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    geometry = Column(Text, nullable=True)
    area = Column(Float, nullable=True)
    status = Column(SAEnum(ProjectStatus), default=ProjectStatus.RUNNING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
