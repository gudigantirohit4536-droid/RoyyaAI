import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pond_id: Mapped[str] = mapped_column(String, ForeignKey("ponds.id"), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    doc: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Day of Culture (auto-calculated)

    # Water Quality
    dissolved_oxygen: Mapped[float | None] = mapped_column(Float, nullable=True)   # mg/L
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    salinity: Mapped[float | None] = mapped_column(Float, nullable=True)            # ppt
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)         # °C
    alkalinity: Mapped[float | None] = mapped_column(Float, nullable=True)          # mg/L
    ammonia: Mapped[float | None] = mapped_column(Float, nullable=True)             # mg/L
    nitrite: Mapped[float | None] = mapped_column(Float, nullable=True)             # mg/L
    secchi_depth: Mapped[float | None] = mapped_column(Float, nullable=True)        # cm

    # Feeding
    feed_quantity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    feed_brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feed_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Growth & Mortality
    abw_grams: Mapped[float | None] = mapped_column(Float, nullable=True)           # Average Body Weight
    mortality_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sampling_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    pond: Mapped["Pond"] = relationship("Pond", back_populates="daily_logs")
