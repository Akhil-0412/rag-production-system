from fastapi import APIRouter
from app.services.monitoring import MonitoringService

router = APIRouter()
monitor = MonitoringService()

@router.get("/recent")
async def get_recent_metrics(limit: int = 20):
    return monitor.get_recent_metrics(limit=limit)
