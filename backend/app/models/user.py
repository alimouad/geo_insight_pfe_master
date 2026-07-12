import enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SAEnum(UserRole, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=UserRole.USER,
        nullable=False,
    )
    avatar = Column(String(500), nullable=True)
    organization = Column(String(255), nullable=True)
    country = Column(String(120), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    theme = Column(String(20), nullable=False, default="light")
    language = Column(String(10), nullable=False, default="en")
    default_basemap = Column(String(50), nullable=False, default="OpenStreetMap")
    default_projection = Column(String(20), nullable=False, default="EPSG:4326")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")