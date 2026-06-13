from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user_id, get_current_org_id
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse, PondCreate, PondUpdate, PondResponse, StockingCreate, StockingResponse
from app.services.farm_service import FarmService

router = APIRouter()


# ─── Farms ───────────────────────────────────────────────

@router.post("", response_model=FarmResponse, status_code=201)
async def create_farm(
    data: FarmCreate,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).create_farm(data)


@router.get("", response_model=list[FarmResponse])
async def list_farms(
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).list_farms()


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).get_farm(farm_id)


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: str,
    data: FarmUpdate,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).update_farm(farm_id, data)


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    await FarmService(db, org_id).delete_farm(farm_id)


# ─── Ponds ───────────────────────────────────────────────

@router.post("/{farm_id}/ponds", response_model=PondResponse, status_code=201)
async def create_pond(
    farm_id: str,
    data: PondCreate,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).create_pond(farm_id, data)


@router.get("/{farm_id}/ponds", response_model=list[PondResponse])
async def list_ponds(
    farm_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).list_ponds(farm_id)


@router.get("/ponds/{pond_id}", response_model=PondResponse)
async def get_pond(
    pond_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).get_pond(pond_id)


@router.put("/ponds/{pond_id}", response_model=PondResponse)
async def update_pond(
    pond_id: str,
    data: PondUpdate,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).update_pond(pond_id, data)


@router.delete("/ponds/{pond_id}", status_code=204)
async def delete_pond(
    pond_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    await FarmService(db, org_id).delete_pond(pond_id)


# ─── Stockings ───────────────────────────────────────────

@router.post("/ponds/{pond_id}/stockings", response_model=StockingResponse, status_code=201)
async def add_stocking(
    pond_id: str,
    data: StockingCreate,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).add_stocking(pond_id, data)


@router.get("/ponds/{pond_id}/stockings/active", response_model=StockingResponse | None)
async def get_active_stocking(
    pond_id: str,
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
):
    return await FarmService(db, org_id).get_active_stocking(pond_id)
