import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Text, Date, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base


class PondStatus(str, enum.Enum):
    ACTIVE = "active"
    HARVESTED = "harvested"
    FALLOW = "fallow"
    PREPARATION = "preparation"


class Pond(Base):
    __tablename__ = "ponds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String, ForeignKey("farms.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth_feet: Mapped[float | None] = mapped_column(Float, nullable=True)
    pond_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # lined, unlined, hdpe
    water_source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # canal, bore, sea
    status: Mapped[PondStatus] = mapped_column(
        SAEnum(PondStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=PondStatus.PREPARATION,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    farm: Mapped["Farm"] = relationship("Farm", back_populates="ponds")
    stockings: Mapped[list["Stocking"]] = relationship("Stocking", back_populates="pond", cascade="all, delete-orphan")
    daily_logs: Mapped[list["DailyLog"]] = relationship("DailyLog", back_populates="pond", cascade="all, delete-orphan")


class Stocking(Base):
    __tablename__ = "stockings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pond_id: Mapped[str] = mapped_column(String, ForeignKey("ponds.id"), nullable=False, index=True)
    stocking_date: Mapped[date] = mapped_column(Date, nullable=False)
    pl_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stocking_density: Mapped[float | None] = mapped_column(Float, nullable=True)  # PL per sqm
    pl_source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # hatchery name
    pl_age_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pond: Mapped["Pond"] = relationship("Pond", back_populates="stockings")
