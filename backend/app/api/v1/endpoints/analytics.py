from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_org_id
from app.schemas.analytics import PondSummary, WaterQualityTrend, GrowthTrend
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/ponds/{pond_id}/summary", response_model=PondSummary)
async def pond_summary(
    pond_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsService(db, org_id).get_pond_summary(pond_id)


@router.get("/ponds/{pond_id}/water-quality", response_model=WaterQualityTrend)
async def water_quality_trend(
    pond_id: str,
    days: int = Query(default=30, le=120),
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsService(db, org_id).get_water_quality_trend(pond_id, days)


@router.get("/ponds/{pond_id}/growth", response_model=GrowthTrend)
async def growth_trend(
    pond_id: str,
    days: int = Query(default=30, le=120),
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsService(db, org_id).get_growth_trend(pond_id, days)
