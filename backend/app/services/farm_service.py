from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.models.farm import Farm
from app.models.pond import Pond, Stocking
from app.models.daily_log import DailyLog
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse, PondCreate, PondUpdate, PondResponse, StockingCreate, StockingResponse
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse
from app.services.health_scorer import calculate_health_score


class FarmService:
    def __init__(self, db: AsyncSession, organization_id: str):
        self.db = db
        self.org_id = organization_id

    # ─── Farms ───────────────────────────────────────

    async def create_farm(self, data: FarmCreate) -> FarmResponse:
        farm = Farm(organization_id=self.org_id, **data.model_dump())
        self.db.add(farm)
        await self.db.flush()
        return FarmResponse.model_validate(farm)

    async def list_farms(self) -> list[FarmResponse]:
        result = await self.db.execute(select(Farm).where(Farm.organization_id == self.org_id))
        return [FarmResponse.model_validate(f) for f in result.scalars().all()]

    async def get_farm(self, farm_id: str) -> FarmResponse:
        farm = await self._get_farm_or_404(farm_id)
        return FarmResponse.model_validate(farm)

    async def update_farm(self, farm_id: str, data: FarmUpdate) -> FarmResponse:
        farm = await self._get_farm_or_404(farm_id)
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(farm, key, value)
        await self.db.flush()
        return FarmResponse.model_validate(farm)

    async def delete_farm(self, farm_id: str) -> None:
        farm = await self._get_farm_or_404(farm_id)
        await self.db.delete(farm)

    async def _get_farm_or_404(self, farm_id: str) -> Farm:
        result = await self.db.execute(
            select(Farm).where(Farm.id == farm_id, Farm.organization_id == self.org_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
        return farm

    # ─── Ponds ───────────────────────────────────────

    async def create_pond(self, farm_id: str, data: PondCreate) -> PondResponse:
        await self._get_farm_or_404(farm_id)
        pond = Pond(farm_id=farm_id, **data.model_dump())
        self.db.add(pond)
        await self.db.flush()
        return PondResponse.model_validate(pond)

    async def list_ponds(self, farm_id: str) -> list[PondResponse]:
        await self._get_farm_or_404(farm_id)
        result = await self.db.execute(select(Pond).where(Pond.farm_id == farm_id))
        return [PondResponse.model_validate(p) for p in result.scalars().all()]

    async def get_pond(self, pond_id: str) -> PondResponse:
        pond = await self._get_pond_or_404(pond_id)
        return PondResponse.model_validate(pond)

    async def update_pond(self, pond_id: str, data: PondUpdate) -> PondResponse:
        pond = await self._get_pond_or_404(pond_id)
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(pond, key, value)
        await self.db.flush()
        return PondResponse.model_validate(pond)

    async def delete_pond(self, pond_id: str) -> None:
        pond = await self._get_pond_or_404(pond_id)
        await self.db.delete(pond)

    async def _get_pond_or_404(self, pond_id: str) -> Pond:
        result = await self.db.execute(
            select(Pond).join(Farm).where(Pond.id == pond_id, Farm.organization_id == self.org_id)
        )
        pond = result.scalar_one_or_none()
        if not pond:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pond not found")
        return pond

    # ─── Stockings ───────────────────────────────────

    async def add_stocking(self, pond_id: str, data: StockingCreate) -> StockingResponse:
        await self._get_pond_or_404(pond_id)
        # Deactivate previous stockings
        prev = await self.db.execute(select(Stocking).where(Stocking.pond_id == pond_id, Stocking.is_active == True))
        for s in prev.scalars().all():
            s.is_active = False
        stocking = Stocking(pond_id=pond_id, **data.model_dump())
        self.db.add(stocking)
        await self.db.flush()
        return StockingResponse.model_validate(stocking)

    async def get_active_stocking(self, pond_id: str) -> StockingResponse | None:
        result = await self.db.execute(
            select(Stocking).where(Stocking.pond_id == pond_id, Stocking.is_active == True)
        )
        stocking = result.scalar_one_or_none()
        return StockingResponse.model_validate(stocking) if stocking else None

    # ─── Daily Logs ──────────────────────────────────

    async def add_daily_log(self, pond_id: str, data: DailyLogCreate, user_id: str) -> DailyLogResponse:
        await self._get_pond_or_404(pond_id)

        # Calculate DOC from active stocking
        doc = None
        stocking_result = await self.db.execute(
            select(Stocking).where(Stocking.pond_id == pond_id, Stocking.is_active == True)
        )
        stocking = stocking_result.scalar_one_or_none()
        if stocking:
            doc = (data.log_date - stocking.stocking_date).days

        health = calculate_health_score(
            dissolved_oxygen=data.dissolved_oxygen,
            ph=data.ph,
            salinity=data.salinity,
            temperature=data.temperature,
            alkalinity=data.alkalinity,
            ammonia=data.ammonia,
            nitrite=data.nitrite,
            secchi_depth=data.secchi_depth,
        )

        log = DailyLog(
            pond_id=pond_id,
            doc=doc,
            created_by=user_id,
            health_score=health.score,
            health_status=health.status,
            **data.model_dump(),
        )
        self.db.add(log)
        await self.db.flush()
        return DailyLogResponse.model_validate(log)

    async def list_daily_logs(self, pond_id: str, limit: int = 30) -> list[DailyLogResponse]:
        await self._get_pond_or_404(pond_id)
        result = await self.db.execute(
            select(DailyLog)
            .where(DailyLog.pond_id == pond_id)
            .order_by(DailyLog.log_date.desc())
            .limit(limit)
        )
        return [DailyLogResponse.model_validate(l) for l in result.scalars().all()]
