from pydantic import BaseModel
from datetime import date


class PondSummary(BaseModel):
    pond_id: str
    pond_name: str
    doc: int | None
    current_health_score: float | None
    current_health_status: str | None
    latest_abw_grams: float | None
    estimated_biomass_kg: float | None
    total_feed_kg: float | None
    running_fcr: float | None
    total_mortality: int | None
    stocking_date: date | None
    pl_count: int | None
    days_to_harvest: int | None


class WaterQualityPoint(BaseModel):
    log_date: date
    doc: int | None
    dissolved_oxygen: float | None
    ph: float | None
    temperature: float | None
    salinity: float | None
    alkalinity: float | None
    ammonia: float | None
    nitrite: float | None
    secchi_depth: float | None
    health_score: float | None


class GrowthPoint(BaseModel):
    log_date: date
    doc: int | None
    abw_grams: float | None
    feed_quantity_kg: float | None
    mortality_count: int | None


class WaterQualityTrend(BaseModel):
    pond_id: str
    days: int
    data: list[WaterQualityPoint]


class GrowthTrend(BaseModel):
    pond_id: str
    days: int
    data: list[GrowthPoint]
