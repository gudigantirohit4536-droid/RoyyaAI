from pydantic import BaseModel
from datetime import datetime, date
from app.models.pond import PondStatus


# ─── Farm ──────────────────────────────────────────

class FarmCreate(BaseModel):
    name: str
    location: str | None = None
    district: str | None = None
    state: str | None = None
    total_area_acres: float | None = None
    notes: str | None = None


class FarmUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    district: str | None = None
    state: str | None = None
    total_area_acres: float | None = None
    notes: str | None = None


class FarmResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    location: str | None
    district: str | None
    state: str | None
    total_area_acres: float | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Pond ──────────────────────────────────────────

class PondCreate(BaseModel):
    name: str
    area_acres: float | None = None
    depth_feet: float | None = None
    pond_type: str | None = None
    water_source: str | None = None
    notes: str | None = None


class PondUpdate(BaseModel):
    name: str | None = None
    area_acres: float | None = None
    depth_feet: float | None = None
    pond_type: str | None = None
    water_source: str | None = None
    status: PondStatus | None = None
    notes: str | None = None


class PondResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    area_acres: float | None
    depth_feet: float | None
    pond_type: str | None
    water_source: str | None
    status: PondStatus
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Stocking ──────────────────────────────────────

class StockingCreate(BaseModel):
    stocking_date: date
    pl_count: int | None = None
    stocking_density: float | None = None
    pl_source: str | None = None
    pl_age_days: int | None = None
    seed_cost: float | None = None
    notes: str | None = None


class StockingResponse(BaseModel):
    id: str
    pond_id: str
    stocking_date: date
    pl_count: int | None
    stocking_density: float | None
    pl_source: str | None
    pl_age_days: int | None
    seed_cost: float | None
    is_active: bool
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
