from pydantic import BaseModel
from datetime import datetime, date


class DailyLogCreate(BaseModel):
    log_date: date
    dissolved_oxygen: float | None = None
    ph: float | None = None
    salinity: float | None = None
    temperature: float | None = None
    alkalinity: float | None = None
    ammonia: float | None = None
    nitrite: float | None = None
    secchi_depth: float | None = None
    feed_quantity_kg: float | None = None
    feed_brand: str | None = None
    feed_type: str | None = None
    abw_grams: float | None = None
    mortality_count: int | None = None
    sampling_count: int | None = None
    notes: str | None = None


class DailyLogResponse(BaseModel):
    id: str
    pond_id: str
    log_date: date
    doc: int | None
    dissolved_oxygen: float | None
    ph: float | None
    salinity: float | None
    temperature: float | None
    alkalinity: float | None
    ammonia: float | None
    nitrite: float | None
    secchi_depth: float | None
    feed_quantity_kg: float | None
    feed_brand: str | None
    feed_type: str | None
    abw_grams: float | None
    mortality_count: int | None
    sampling_count: int | None
    health_score: float | None
    health_status: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
