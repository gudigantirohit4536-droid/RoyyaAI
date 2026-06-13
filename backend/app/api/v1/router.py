from fastapi import APIRouter
from app.api.v1.endpoints import auth, farms, ponds, logs, ai, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_router.include_router(ponds.router, prefix="/ponds", tags=["Ponds"])
api_router.include_router(logs.router, prefix="/logs", tags=["Daily Logs"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
