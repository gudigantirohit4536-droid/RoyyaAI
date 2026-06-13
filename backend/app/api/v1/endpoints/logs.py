from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user_id, get_current_org_id
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse
from app.services.farm_service import FarmService

router = APIRouter()


@router.post("/ponds/{pond_id}", response_model=DailyLogResponse, status_code=201)
async def add_daily_log(
    pond_id: str,
    data: DailyLogCreate,
    user_id: str = Depends(get_current_user_id),
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).add_daily_log(pond_id, data, user_id)


@router.get("/ponds/{pond_id}", response_model=list[DailyLogResponse])
async def list_daily_logs(
    pond_id: str,
    limit: int = Query(default=30, le=90),
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).list_daily_logs(pond_id, limit)
