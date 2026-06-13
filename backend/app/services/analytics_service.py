from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.farm import Farm
from app.models.pond import Pond, Stocking
from app.models.daily_log import DailyLog
from app.schemas.analytics import (
    PondSummary, WaterQualityTrend, GrowthTrend,
    WaterQualityPoint, GrowthPoint,
)

HARVEST_TARGET_ABW = 20.0  # grams — typical harvest target


class AnalyticsService:
    def __init__(self, db: AsyncSession, org_id: str):
        self.db = db
        self.org_id = org_id

    async def get_pond_summary(self, pond_id: str) -> PondSummary:
        pond = await self._get_pond_or_404(pond_id)

        stocking_result = await self.db.execute(
            select(Stocking).where(Stocking.pond_id == pond_id, Stocking.is_active == True)
        )
        stocking = stocking_result.scalar_one_or_none()

        logs_result = await self.db.execute(
            select(DailyLog)
            .where(DailyLog.pond_id == pond_id)
            .order_by(DailyLog.log_date.desc())
        )
        logs = logs_result.scalars().all()

        latest_log = logs[0] if logs else None

        total_feed_kg = sum(l.feed_quantity_kg or 0 for l in logs)
        total_mortality = sum(l.mortality_count or 0 for l in logs)

        # Estimated biomass from latest ABW and survival
        estimated_biomass = None
        running_fcr = None
        if stocking and latest_log and latest_log.abw_grams:
            surviving = (stocking.pl_count or 0) - total_mortality
            estimated_biomass = round((surviving * latest_log.abw_grams) / 1000, 1)
            if estimated_biomass > 0 and total_feed_kg > 0:
                running_fcr = round(total_feed_kg / estimated_biomass, 2)

        # Days to harvest estimate
        days_to_harvest = None
        if latest_log and latest_log.abw_grams and latest_log.doc:
            abw = latest_log.abw_grams
            if abw < HARVEST_TARGET_ABW:
                growth_per_day = abw / latest_log.doc if latest_log.doc > 0 else 0.15
                if growth_per_day > 0:
                    days_to_harvest = int((HARVEST_TARGET_ABW - abw) / growth_per_day)

        return PondSummary(
            pond_id=pond_id,
            pond_name=pond.name,
            doc=latest_log.doc if latest_log else None,
            current_health_score=latest_log.health_score if latest_log else None,
            current_health_status=latest_log.health_status if latest_log else None,
            latest_abw_grams=latest_log.abw_grams if latest_log else None,
            estimated_biomass_kg=estimated_biomass,
            total_feed_kg=round(total_feed_kg, 1) if total_feed_kg else None,
            running_fcr=running_fcr,
            total_mortality=total_mortality,
            stocking_date=stocking.stocking_date if stocking else None,
            pl_count=stocking.pl_count if stocking else None,
            days_to_harvest=days_to_harvest,
        )

    async def get_water_quality_trend(self, pond_id: str, days: int = 30) -> WaterQualityTrend:
        await self._get_pond_or_404(pond_id)
        result = await self.db.execute(
            select(DailyLog)
            .where(DailyLog.pond_id == pond_id)
            .order_by(DailyLog.log_date.asc())
            .limit(days)
        )
        logs = result.scalars().all()
        data = [
            WaterQualityPoint(
                log_date=l.log_date,
                doc=l.doc,
                dissolved_oxygen=l.dissolved_oxygen,
                ph=l.ph,
                temperature=l.temperature,
                salinity=l.salinity,
                alkalinity=l.alkalinity,
                ammonia=l.ammonia,
                nitrite=l.nitrite,
                secchi_depth=l.secchi_depth,
                health_score=l.health_score,
            )
            for l in logs
        ]
        return WaterQualityTrend(pond_id=pond_id, days=days, data=data)

    async def get_growth_trend(self, pond_id: str, days: int = 30) -> GrowthTrend:
        await self._get_pond_or_404(pond_id)
        result = await self.db.execute(
            select(DailyLog)
            .where(DailyLog.pond_id == pond_id)
            .order_by(DailyLog.log_date.asc())
            .limit(days)
        )
        logs = result.scalars().all()
        data = [
            GrowthPoint(
                log_date=l.log_date,
                doc=l.doc,
                abw_grams=l.abw_grams,
                feed_quantity_kg=l.feed_quantity_kg,
                mortality_count=l.mortality_count,
            )
            for l in logs
        ]
        return GrowthTrend(pond_id=pond_id, days=days, data=data)

    async def _get_pond_or_404(self, pond_id: str) -> Pond:
        result = await self.db.execute(
            select(Pond).join(Farm).where(Pond.id == pond_id, Farm.organization_id == self.org_id)
        )
        pond = result.scalar_one_or_none()
        if not pond:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pond not found")
        return pond
